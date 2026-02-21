# Python modules
from typing import Any

# Django modules
from django.db.models import (
    Model,
    DateTimeField,
    QuerySet,
    Manager,
)
from django.utils import timezone as django_timezone


class SoftDeleteQuerySet(QuerySet):
    def soft_delete(
        self, *args: tuple[Any, ...],
        **kwargs: dict[Any, Any]
    ) -> None:
        """Deletes a queryset of objects."""
        self.update(deleted_at=django_timezone.now())


class SoftDeleteManager(
    Manager.from_queryset(SoftDeleteQuerySet)
):
    """Manager that excludes soft-deleted objects."""

    def get_queryset(
        self, *args: tuple[Any, ...],
        **kwargs: dict[Any, Any]
    ) -> QuerySet:
        """Return queryset excluding soft-deleted objects."""
        return super().get_queryset().filter(
            deleted_at__isnull=True,
        )


class AbstractBaseModel(Model):
    """Abstract Base Model with common fields."""

    created_at = DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = DateTimeField(auto_now=True, verbose_name="Updated at")
    deleted_at = DateTimeField(
        null=True,
        blank=True,
        verbose_name="Deleted at"
    )
    objects = SoftDeleteManager()
    all_objects = Manager()

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
