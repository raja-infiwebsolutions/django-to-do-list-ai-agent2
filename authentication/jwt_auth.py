from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from typing import Tuple, Optional
from utils.jwt import verify_access_token
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import logging

logger = logging.getLogger(__name__)


class JWTAuthentication(BaseAuthentication):
    """DRF authentication using JWT tokens in the Authorization header.

    Expects header: Authorization: Bearer <token>
    """

    keyword = "Bearer"

    def authenticate(self, request) -> Optional[Tuple[object, str]]:
        # Support multiple header retrieval methods and be case-insensitive for scheme
        auth_header = ""
        # request.headers is case-insensitive mapping in Django >=2.2
        try:
            auth_header = request.headers.get("Authorization", "")
        except Exception:
            auth_header = ""
        if not auth_header:
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2:
            raise exceptions.AuthenticationFailed("Invalid Authorization header format.")
        scheme, token = parts
        if scheme.lower() != self.keyword.lower():
            return None

        try:
            payload = verify_access_token(token)
        except ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token has expired")
        except InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token")
        except Exception:
            # Record unexpected internal exception for debugging (no sensitive data)
            logger.exception("Unexpected error during JWT authentication")
            raise exceptions.AuthenticationFailed("Authentication failed")

        user_id = payload.get("user_id")
        if not user_id:
            raise exceptions.AuthenticationFailed("Invalid token payload.")

        # Defer getting the User model until runtime to avoid AppRegistryNotReady issues
        User = get_user_model()

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("User not found.")

        # Ensure the user is active
        if not getattr(user, "is_active", True):
            raise exceptions.AuthenticationFailed("User is inactive")

        return (user, token)
