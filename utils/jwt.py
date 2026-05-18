import os
import jwt
import datetime
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# Use a dedicated JWT secret separate from Django SECRET_KEY. Require it in production.
JWT_SECRET = getattr(settings, "JWT_SECRET", None)
if not JWT_SECRET:
    if getattr(settings, "DEBUG", True):
        # For development: prefer environment override or reuse Django SECRET_KEY; if neither
        # exists, generate a runtime-only secret so no secret is committed to source.
        JWT_SECRET = os.environ.get("JWT_SECRET") or getattr(settings, "SECRET_KEY", None)
        if not JWT_SECRET:
            # Runtime-only secret; tokens will be invalidated on process restart which
            # is acceptable for local development.
            JWT_SECRET = os.urandom(32).hex()
    else:
        raise ImproperlyConfigured("JWT_SECRET environment variable is required in production")

JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = int(getattr(settings, "JWT_EXP_DELTA_SECONDS", 60 * 60 * 24))  # default 1 day


def _now_timestamp() -> int:
    return int(datetime.datetime.utcnow().timestamp())


def create_access_token(user_id: int, expires_delta: int = None) -> str:
    """Create a JWT token containing the user_id and expiry using integer timestamps."""
    if expires_delta is None:
        expires_delta = JWT_EXP_DELTA_SECONDS
    iat = _now_timestamp()
    exp = iat + int(expires_delta)
    payload = {
        "user_id": user_id,
        "iat": iat,
        "exp": exp,
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    # PyJWT >= 2 returns str, older versions bytes
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def verify_access_token(token: str) -> dict:
    """Verify a JWT token and return the payload.

    Raises jwt.ExpiredSignatureError, jwt.InvalidTokenError on failure.
    """
    if not token:
        raise jwt.InvalidTokenError("Token is missing")
    # Require standard claims and use integer timestamps
    payload = jwt.decode(
        token,
        JWT_SECRET,
        algorithms=[JWT_ALGORITHM],
        options={"require": ["exp", "iat"]},
    )
    return payload
