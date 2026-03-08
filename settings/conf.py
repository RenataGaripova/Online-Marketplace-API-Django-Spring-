# Project modules
from decouple import config

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
