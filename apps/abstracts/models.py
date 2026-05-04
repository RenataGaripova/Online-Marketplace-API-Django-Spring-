# Python modules
from typing import Any, Generic, TypeVar

# Django modules
from django.db.models import (
    Model,
    DateTimeField,
    QuerySet,
    Manager,
)
from django.db.utils import NotSupportedError
from django.utils import timezone as django_timezone


T = TypeVar("T", bound=Model)


class SoftDeletableQuerySet(QuerySet, Generic[T]):
    """Soft deletable queryset."""

    def _raise_not_supported_error(self, message: str) -> None:
        """Raises a not supported error that doesn't let making a query,"""
        raise NotSupportedError(message)

    def delete(self) -> tuple[int, dict[str, int]]:
        """Soft-deletes a queryset ob objects,"""
        count: int = self.update(deleted_at=django_timezone.now())
        return count, {self.model._meta.label: count}

    def hard_delete(self) -> int:
        """Deletes a queryset of objects from the DB permanently."""
        return super().delete()

    def get_soft_deleted(self) -> "SoftDeletableQuerySet[T]":
        """Returns soft deleted objects of a Model."""
        return self.filter(deleted_at__isnull=False)

    def get_not_deleted(self) -> "SoftDeletableQuerySet[T]":
        """Returns objects of a Model, excluding soft deleted intances."""
        return self.filter(deleted_at__isnull=True)


class AbstractBaseModel(Model):
    """Abstract Base Model with common fields."""

    created_at: DateTimeField = DateTimeField(
        auto_now_add=True, verbose_name="Created at"
    )
    updated_at: DateTimeField = DateTimeField(
        auto_now=True, verbose_name="Updated at"
    )
    deleted_at: DateTimeField = DateTimeField(
        null=True, blank=True, verbose_name="Deleted at"
    )
    objects: Manager = SoftDeletableQuerySet.as_manager()

    class Meta:
        """Meta class."""

        abstract = True

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def delete(self, *args: tuple[Any, ...], **kwargs: dict[Any, Any]) -> None:
        """Soft delete the model's object."""
        self.deleted_at = django_timezone.now()
        self.save(update_fields=["deleted_at"])

    def hard_delete(
        self, using: Any = None, keep_parents: bool = False
    ) -> None:
        """Delete an instance from the DB."""
        super().delete(
            using=using,
            keep_parents=keep_parents,
        )
