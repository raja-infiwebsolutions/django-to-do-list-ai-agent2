from typing import Tuple, Dict, Any, Optional
import logging

from django.contrib.auth import authenticate, get_user_model
from django.db import IntegrityError

from utils.jwt import create_access_token
from apps.todos.serializers import SignupSerializer

logger = logging.getLogger(__name__)
User = get_user_model()


def register_user(data: Dict[str, Any]) -> Tuple[Optional[User], Optional[Dict[str, Any]]]:
    """Register a new user using the SignupSerializer.

    Returns (user, errors). On success errors is None.
    """
    serializer = SignupSerializer(data=data)
    if not serializer.is_valid():
        return None, serializer.errors
    try:
        user = serializer.save()
        return user, None
    except IntegrityError:
        return None, {"email": ["A user with this email already exists."]}
    except Exception as exc:
        # Log the full exception server-side for diagnostics, but don't return internals to clients
        logger.exception("Unexpected error creating user: %s", exc)
        return None, {"non_field_errors": ["Unable to create user at this time"]}


def login_user(email: str, password: str) -> Tuple[Optional[User], Optional[str], Optional[str]]:
    """Authenticate user and return (user, token, error_message).

    On success returns (user, token, None). On failure returns (None, None, message).
    """
    email_norm = (email or "").strip().lower()
    # Try to authenticate via username/email depending on backend
    user = authenticate(username=email_norm, password=password)
    if not user:
        # try email kwarg (some custom backends accept this)
        user = authenticate(email=email_norm, password=password)

    if not user:
        return None, None, "Invalid credentials"
    if not getattr(user, "is_active", True):
        return None, None, "User account is disabled"

    # create JWT
    token = create_access_token(user_id=user.id)
    return user, token, None


def generate_jwt_for_user(user: User) -> str:
    return create_access_token(user_id=user.id)


def verify_jwt(token: str) -> Dict[str, Any]:
    # Proxy to utils.jwt.verify_access_token (keeps service surface)
    from utils.jwt import verify_access_token

    return verify_access_token(token)
