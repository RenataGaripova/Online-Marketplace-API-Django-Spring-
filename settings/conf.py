# Python modules
import os

# Project modules
from decouple import config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ----------------------------------------------
# Env id
#
ENV_POSSIBLE_OPTIONS = (
    "local",
    "prod",
)
ENV_ID = config("PROJECT_ENV_ID")
SECRET_KEY = (
    "django-insecure--!sazwabf2m!-q#8ui0rlql_@^cii54s9cuu6@hhzli(-#yk_@"
)
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
