"""
Django settings for the card auction platform.
"""

from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
)

# In Docker, env vars come from `env_file:` in docker-compose.yml.
# Locally (e.g. running manage.py from a venv), fall back to the repo-root .env.
_root_env_file = BASE_DIR.parent / ".env"
if _root_env_file.exists():
    environ.Env.read_env(_root_env_file)

SECRET_KEY = env("DJANGO_SECRET_KEY", default="django-insecure-dev-only-change-me")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "accounts",
    "cards",
    "inventory",
    "auctions",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
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
        "DIRS": [],
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
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", default="auction_db"),
        "USER": env("POSTGRES_USER", default="auction_user"),
        "PASSWORD": env("POSTGRES_PASSWORD", default="postgres"),
        "HOST": env("POSTGRES_HOST", default="localhost"),
        "PORT": env("POSTGRES_PORT", default="5432"),
    }
}

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Base URL used to build absolute media (card image) URLs. This must be
# reachable from wherever Next.js's *server-side* image optimizer runs —
# next/image always proxies images through a server-side fetch
# (/_next/image?url=...) regardless of whether the page itself was server-
# or client-rendered, so it needs the Docker-internal address
# (http://backend:8000, matching the frontend's INTERNAL_API_URL), not the
# browser-facing one. Outside Docker (plain `manage.py runserver`), default
# to localhost since there's no separate internal hostname.
MEDIA_BASE_URL = env("MEDIA_BASE_URL", default="http://localhost:8000")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# CORS — the frontend runs on a different origin (localhost:3000) and needs
# to send/receive the httpOnly auth cookies, so credentials must be allowed.
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = env.list(
    "DJANGO_CORS_ALLOWED_ORIGINS", default=["http://localhost:3000"]
)
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = env.list(
    "DJANGO_CORS_ALLOWED_ORIGINS", default=["http://localhost:3000"]
)

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "accounts.authentication.CookieJWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_PAGINATION_CLASS": "config.pagination.DefaultPagination",
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
}

# ---------------------------------------------------------------------------
# JWT — issued by SimpleJWT, transported as httpOnly cookies (never exposed
# to JS). See accounts/authentication.py and accounts/views.py.
# ---------------------------------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=env.int("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", default=15)
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=env.int("JWT_REFRESH_TOKEN_LIFETIME_DAYS", default=7)
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "SIGNING_KEY": env("JWT_SIGNING_KEY", default=SECRET_KEY),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

JWT_AUTH_COOKIE = "access_token"
JWT_REFRESH_COOKIE = "refresh_token"
JWT_COOKIE_SECURE = env.bool("JWT_COOKIE_SECURE", default=False)
JWT_COOKIE_SAMESITE = env("JWT_COOKIE_SAMESITE", default="Lax")
JWT_COOKIE_PATH = "/"

AUTH_COOKIE_DOMAIN = None
