# Python modules
import os
from datetime import timedelta
from decouple import config
from django.core.management.utils import get_random_secret_key

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ----------------------------------------------
# Env id
#
ENV_POSSIBLE_OPTIONS = (
    "local",
    "prod",
)
ENV_ID = config("PROJECT_ENV_ID", "locel")
SECRET_KEY = config("SECRET_KEY", get_random_secret_key())
# ----------------------------------------------
# DRF Spectacular
#
SPECTACULAR_SETTINGS = {
    "TITLE": "Online Marketplace API",
    "DESCRIPTION": "Django Project",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    # OTHER SETTINGS
}
# ----------------------------------------------
# Rest Framework
#
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.ScopedRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "register": "10/min",
        "otp": "3/min",
    },
}
# ----------------------------------------------
# JWT Authorization
#
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("JWT",),
}
# ----------------------------------------------
# LOGGING
#
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    # Filters
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        }
    },
    # Formatters
    "formatters": {
        "verbose": {
            "format": "[{asctime}], {levelname} - {name} - {module}: {message}.",
            "style": "{",
        },
        "simple": {
            "format": "{levelname}: {message}.",
            "style": "{",
        },
    },
    # Handlers
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "WARNING",
            "filename": os.path.join(BASE_DIR, "logs/app.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "formatter": "verbose",
        },
        "debug_only_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "filename": os.path.join(BASE_DIR, "logs/debug_requests.log"),
            "filters": ["require_debug_true"],
            "formatter": "verbose",
        },
    },
    # Loggers
    "loggers": {
        "users": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "products": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "orders": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["file"],
            "level": "WARNING",
            "propagate": False,
        },
        "debug_requests": {
            "handlers": ["debug_only_file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
# ------------------------------------------------
# Redis Configuration
#
REDIS_HOST = config("REDIS_HOST", cast=str, default="localhost")
REDIS_PORT = config("REDIS_PORT", cast=int, default=6379)
REDIS_CELERY_DB = config("REDIS_CELERY_DB", cast=int, default=0)
REDIS_DB = config("REDIS_DB", cast=int, default=1)
REDIS_SSE_DB = config("REDIS_SSE_DB", cast=int, default=2)

# ------------------------------------------------
# Cache (Redis)
#
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
    }
}

# ------------------------------------------------
# Celery
#
CELERY_BROKER_URL = (
    f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
)
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TIMEZONE = "UTC"

# ------------------------------------------------
# Email (console backend is fine for a student project)
#
EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL",
    default="noreply@marketplace.local",
)
