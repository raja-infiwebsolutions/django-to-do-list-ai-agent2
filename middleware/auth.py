from typing import Callable, Any, Dict
from django.http import JsonResponse
from utils.jwt import verify_access_token
from django.contrib.auth import get_user_model
from utils.response import error_response
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


def require_auth(handler: Callable[[Any, Dict[str, Any]], JsonResponse]):
    """Wrapper for Django REST-style view functions to enforce JWT auth.

    Expects Authorization header 'Bearer <token>'. Attaches `user` to request.
    """

    def _wrapped(request, *args, **kwargs):
        # Prefer META for older Django compatibility, fall back to request.headers
        auth_header = request.META.get('HTTP_AUTHORIZATION') or getattr(request, 'headers', {}).get('Authorization')
        if not auth_header:
            return error_response(message="Authorization header missing", status=401)
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return error_response(message="Invalid Authorization header", status=401)
        token = parts[1]
        try:
            payload = verify_access_token(token)
        except Exception as exc:
            # Avoid swallowing critical BaseExceptions
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            # Log token verification failures for diagnostics without exposing internals
            logger.warning("Token verification failed: %s", str(exc))
            return error_response(message="Invalid or expired token", status=401)
        user_id = payload.get("user_id")
        if not user_id:
            return error_response(message="Invalid token payload", status=401)
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return error_response(message="User not found", status=401)
        # Attach user for downstream handlers that rely on request.user
        request.user = user
        return handler(request, *args, **kwargs)

    return _wrapped
