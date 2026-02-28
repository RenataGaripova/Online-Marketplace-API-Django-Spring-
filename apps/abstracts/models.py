# Python modules
from typing import Any

# Django modules
from django.db.models import (
    Model,
    DateTimeField
)
from django.utils import timezone as django_timezone


class AbstractBaseModel(Model):
    """Abstract Base Model with common fields."""

    created_at = DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = DateTimeField(auto_now=True, verbose_name="Updated at")
    deleted_at = DateTimeField(
        null=True,
        blank=True,
        verbose_name="Deleted at"
    )

    class Meta:
        """Meta class."""

        abstract = True

    def soft_delete(
        self, *args: tuple[Any, ...],
        **kwargs: dict[Any, Any]
    ) -> None:
        """Soft delete the model's object."""
        self.deleted_at = django_timezone.now()
        self.save(update_fields=["deleted_at"])
