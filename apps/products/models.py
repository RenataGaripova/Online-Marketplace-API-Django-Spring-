# Django modules
from django.db import models
from django.db.models import (
    CharField,
    TextField,
    ManyToManyField,
    ImageField,
    CASCADE,
    ForeignKey,
    IntegerField,
    DecimalField,
    UniqueConstraint,
    Manager,
)
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

# Project modules
from apps.abstracts.models import AbstractBaseModel


class SoftDeleteManager(Manager):
    """Manager that excludes soft-deleted objects."""

    def get_queryset(self) -> QuerySet:
        """Return queryset excluding soft-deleted objects."""
        return super().get_queryset().filter(deleted_at__isnull=True)


class Category(AbstractBaseModel):
    """
    Category database (table) model.
    """
    MAX_NAME_LENGTH = 100

    name = CharField(max_length=MAX_NAME_LENGTH, unique=True)
    description = TextField(blank=True, null=True)

    objects = SoftDeleteManager()
    all_objects = Manager()

    def __str__(self) -> str:
        """Returns the string representation of the object."""
        return self.name

    def clean(self) -> None:
        """Validate the model."""
        super().clean()
        if self.name and len(self.name) > self.MAX_NAME_LENGTH:
            raise ValidationError(
                f"Category name can't exceed {self.MAX_NAME_LENGTH} characters"
            )

    def save(self, *args, **kwargs) -> None:
        """Override save to call full_clean."""
        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> None:
        """Override delete to perform soft delete and cascade to products."""
        # Soft delete all related products first
        for product in self.products.all():
            product.soft_delete()
        self.soft_delete()


class Product(AbstractBaseModel):
    """
    Product database (table) model.
    """
    MAX_NAME_LENGTH = 100
    MAX_PRICE_DIGITS = 10
    MAX_DECIMAL_PLACES = 2

    category = ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products')
    name = CharField(max_length=MAX_NAME_LENGTH)
    description = TextField(blank=True, null=True)
    price = DecimalField(
        max_digits=MAX_PRICE_DIGITS,
        decimal_places=MAX_DECIMAL_PLACES
    )
    image = ImageField(upload_to='products/', blank=True, null=True)

    objects = SoftDeleteManager()
    all_objects = Manager()

    def __str__(self) -> str:
        """Returns the string representation of the object."""
        return self.name

    def clean(self):
        """Validate the model."""
        super().clean()
        if self.name and len(self.name) > self.MAX_NAME_LENGTH:
            raise ValidationError(
                f"Product name cannot exceed {self.MAX_NAME_LENGTH} characters"
            )
        if self.price is not None and self.price < 0:
            raise ValidationError("Product price cannot be negative")

    def save(self, *args, **kwargs):
        """Override save to call full_clean."""
        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Override delete to perform soft delete
        and cascade to store relations."""
        # Soft delete all related store product relations first
        from apps.products.models import StoreProductRelation
        for relation in StoreProductRelation.objects.filter(product=self):
            relation.soft_delete()
        self.soft_delete()


# New
class Store(AbstractBaseModel):
    """
    Store database (table) model.
    """
    MAX_Store_NAME_LENGTH = 128

    owner = ForeignKey(
        to=get_user_model(),
        on_delete=CASCADE,
        verbose_name="Owner",
    )
    name = CharField(
        max_length=MAX_Store_NAME_LENGTH,
        verbose_name="Store's name"
    )
    description = TextField(
        verbose_name="Description",
    )
    products = ManyToManyField(
        to="Product",
        through=("StoreProductRelation"),
        related_name="stores",
        verbose_name="Available products",
    )

    objects = SoftDeleteManager()
    all_objects = Manager()

    class Meta:
        """Meta class."""

        ordering = ('-created_at',)

    def __str__(self) -> str:
        """Magic str method."""
        return self.name

    def delete(self, *args, **kwargs):
        """Override delete to perform soft delete and
        cascade to store relations."""
        # Soft delete all related store product relations first
        from apps.products.models import StoreProductRelation
        for relation in StoreProductRelation.objects.filter(store=self):
            relation.soft_delete()
        self.soft_delete()


class StoreProductRelation(AbstractBaseModel):
    """Many to many relation table for products and Stores."""
    MAX_NAME_LENGTH = 100
    MAX_PRICE_DIGITS = 10
    MAX_DECIMAL_PLACES = 2

    product = ForeignKey(
        to=Product,
        on_delete=CASCADE,
        verbose_name="Product",
    )
    store = ForeignKey(
        to=Store,
        on_delete=CASCADE,
        verbose_name="Store",
    )
    quantity = IntegerField(
        verbose_name="In stock",
    )
    price = DecimalField(
        max_digits=MAX_PRICE_DIGITS,
        decimal_places=MAX_DECIMAL_PLACES,
        verbose_name="Price",
    )

    objects = SoftDeleteManager()
    all_objects = Manager()

    class Meta:
        """Meta class."""

        constraints = [
            UniqueConstraint(
                fields=["product", "store"],
                name="unique_product_per_store",
            )
        ]

    def clean(self):
        """Validate the model."""
        super().clean()
        if self.quantity is not None and self.quantity < 0:
            raise ValidationError("Quantity cannot be negative")
        if self.price is not None and self.price < 0:
            raise ValidationError("Price cannot be negative")

    def save(self, *args, **kwargs):
        """Override save to call full_clean."""
        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Override delete to perform soft delete."""
        self.soft_delete()
