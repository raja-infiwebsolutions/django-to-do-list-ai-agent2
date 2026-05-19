import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

# DEBUG should be determined early and support common truthy values
DEBUG = os.environ.get("DEBUG", "1").lower() in ("1", "true", "yes")

# SECRET_KEY must be provided via environment in production
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        # use a clearly development-only fallback when DEBUG=True
        SECRET_KEY = "unsafe-dev-secret"
    else:
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY environment variable is required in production"
        )

# ALLOWED_HOSTS should not default to a permissive wildcard in production
_allowed_hosts_env = os.environ.get("ALLOWED_HOSTS", "")
if _allowed_hosts_env:
    ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts_env.split(",") if h.strip()]
else:
    # In development, allow localhost variants; in production require explicit setting
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"] if DEBUG else []

if not DEBUG and not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "ALLOWED_HOSTS must be set in production via the ALLOWED_HOSTS environment variable"
    )

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "authentication",
    "apps.todos",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Login redirect settings
LOGIN_URL = "auth:login"
LOGIN_REDIRECT_URL = "todos:list"

# Configure REST framework authentication classes. Use JWT in production; allow session/basic in DEBUG for convenience.
if DEBUG:
    DEFAULT_AUTH_CLASSES = [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ]
else:
    DEFAULT_AUTH_CLASSES = ["authentication.jwt_auth.JWTAuthentication"]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": DEFAULT_AUTH_CLASSES,
}

# JWT-related settings (can be overridden via environment)
JWT_SECRET = os.environ.get("JWT_SECRET", SECRET_KEY)
JWT_EXPIRES_IN = int(os.environ.get("JWT_EXPIRES_IN", 3600))  # seconds
JWT_ALLOWED_ALGORITHMS = os.environ.get("JWT_ALLOWED_ALGORITHMS", "HS256").split(",")

# Simple safety check: if running in production ensure JWT_SECRET is not the unsafe dev fallback
if not DEBUG and JWT_SECRET == "unsafe-dev-secret":
    raise ImproperlyConfigured(
        "JWT_SECRET must be set to a secure value in production and must not be the unsafe development secret."
    )
