from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from typing import Tuple, Optional
from utils.jwt import verify_access_token

User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    """DRF authentication using JWT tokens in the Authorization header.

    Expects header: Authorization: Bearer <token>
    """

    keyword = "Bearer"

    def authenticate(self, request) -> Optional[Tuple[object, str]]:
        auth_header = request.headers.get("Authorization") or request.META.get("HTTP_AUTHORIZATION")
        if not auth_header:
            return None
        parts = auth_header.split()
        if len(parts) != 2:
            raise exceptions.AuthenticationFailed("Invalid Authorization header format.")
        scheme, token = parts
        if scheme != self.keyword:
            return None
        try:
            payload = verify_access_token(token)
        except Exception as exc:
            raise exceptions.AuthenticationFailed("Invalid or expired token.")
        user_id = payload.get("user_id")
        if not user_id:
            raise exceptions.AuthenticationFailed("Invalid token payload.")
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("User not found.")
        return (user, token)
