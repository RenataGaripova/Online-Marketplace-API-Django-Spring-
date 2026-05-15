# Django modules
from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.orders"

    def ready(self) -> None:
        from apps.orders import signals  # noqa: F401
