import jwt
import datetime
from django.conf import settings

JWT_SECRET = getattr(settings, "DJANGO_SECRET_KEY", None) or settings.SECRET_KEY
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = int(getattr(settings, "JWT_EXP_DELTA_SECONDS", 60 * 60 * 24))  # default 1 day


def create_access_token(user_id: int, expires_delta: int = None) -> str:
    """Create a JWT token containing the user_id and expiry."""
    if expires_delta is None:
        expires_delta = JWT_EXP_DELTA_SECONDS
    now = datetime.datetime.utcnow()
    payload = {
        "user_id": user_id,
        "iat": now,
        "exp": now + datetime.timedelta(seconds=expires_delta),
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
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return payload
