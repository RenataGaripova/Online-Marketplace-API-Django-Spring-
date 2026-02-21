# Python modules
from typing import Any

# Django modules
from django.db import models, transaction
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
    QuerySet,
    Q,
    PositiveIntegerField,
)
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone as django_timezone

# Project modules
from apps.abstracts.models import AbstractBaseModel


class Category(AbstractBaseModel):
    """
    Category database (table) model.
    """
    MAX_NAME_LENGTH = 100
    MAX_DEPTH = 2

    name = CharField(max_length=MAX_NAME_LENGTH, unique=True)
    description = TextField(blank=True, null=True)
    image = models.ImageField(upload_to="category_images")
    parent = models.ForeignKey(
        "self",
        related_name="subcategories",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    depth = PositiveIntegerField(
        editable=False,
        default=1,
    )

    class Meta:
        """Metadata."""
        verbose_name_plural = "Categories"
        default_related_name = "categories"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        """Returns the string representation of the object."""
        return self.name

    def save(
        self, *args: tuple[Any, ...],
        **kwargs: dict[Any, Any]
    ) -> None:
        """Saves an object of the model."""
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 1

        if self.depth > self.MAX_DEPTH:
            raise ValidationError(
                f"Maximum depth — {self.MAX_DEPTH}"
            )
        super().save(*args, **kwargs)

    @transaction.atomic
    def soft_delete_with_relations(
        self, *args: tuple[Any, ...],
        **kwargs: dict[Any, Any]
    ) -> None:
        """Override delete to perform soft delete and cascade to products."""
        now = django_timezone.now()
        if self.deleted_at:
            return
        self.products.filter(
            deleted_at__isnull=True,
        ).update(deleted_at=now)
        self.subcategories.filter(
            deleted_at__isnull=True,
        ).update(deleted_at=now)
        self.deleted_at = now
        self.save(update_fields=["deleted_at"])

    def get_all_products(
        self, *args: tuple[Any, ...],
        **kwargs: dict[Any, Any]
    ) -> QuerySet["Product"]:
        """Get all products from parent category and it's subcategories."""
        direct_subcategories = self.subcategories.all()
        return Product.objects.filter(
            Q(category=self) | Q(category__in=direct_subcategories)
        )

    def count_all_products(self):
        """Get the number of products from parent and it's subcategories."""
        return self.get_all_products().count()


class Product(AbstractBaseModel):
    """
    Product database (table) model.
    """
    MAX_NAME_LENGTH = 100
    MAX_PRICE_DIGITS = 10
    MAX_DECIMAL_PLACES = 2
    MIN_PRICE = 0.1

    category = ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products")
    name = CharField(max_length=MAX_NAME_LENGTH)
    description = TextField(blank=True, null=True)
    price = DecimalField(
        max_digits=MAX_PRICE_DIGITS,
        decimal_places=MAX_DECIMAL_PLACES,
    )
    image = ImageField(upload_to="products/", blank=True, null=True)

    class Meta:
        """Meta class."""

        default_related_name = "products"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        """Returns the string representation of the object."""
        return self.name

    def clean(self):
        """Validate the model."""
        super().clean()
        if self.price < self.MIN_PRICE:
            raise ValidationError("Product price cannot be negative")

    def save(self, *args, **kwargs):
        """Override save to call full_clean."""
        self.full_clean()
        super().save(*args, **kwargs)

    @transaction.atomic
    def soft_delete_with_relations(
        self, *args: tuple[Any, ...],
        **kwargs: dict[Any, Any]
    ) -> None:
        """
        Override delete to perform soft delete
        and cascade to store products.
        """
        from apps.products.models import StoreProductRelation
        now = django_timezone.now()
        StoreProductRelation.objects.filter(
            product=self,
            deleted_at__isnull=True,
        ).update(deleted_at=now)
        self.deleted_at = now
        self.save(update_fields=["deleted_at"])


# New
class Store(AbstractBaseModel):
    """
    Store database (table) model.
    """
    MAX_STORE_NAME_LENGTH = 128

    owner = ForeignKey(
        to=get_user_model(),
        on_delete=CASCADE,
    )
    name = CharField(
        max_length=MAX_STORE_NAME_LENGTH,
    )
    description = TextField()
    products = ManyToManyField(
        to="Product",
        through=("StoreProductRelation"),
        related_name="stores",
    )

    class Meta:
        """Meta class."""

        default_related_name = "stores"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        """Magic str method."""
        return self.name

    @transaction.atomic
    def soft_delete_with_relations(
        self, *args: tuple[Any, ...],
        **kwargs: dict[Any, Any]
    ) -> None:
        """
        Override delete to perform soft delete
        and cascade to store products.
        """
        from apps.products.models import StoreProductRelation
        now = django_timezone.now()
        StoreProductRelation.objects.filter(
            store=self,
            deleted_at__isnull=True,
        ).update(deleted_at=now)
        self.deleted_at = now
        self.save(update_fields=["deleted_at"])


class StoreProductRelation(AbstractBaseModel):
    """Many to many relation table for products and Stores."""
    MAX_NAME_LENGTH = 100
    MAX_PRICE_DIGITS = 10
    MAX_DECIMAL_PLACES = 2
    MIN_PRICE = 0.1

    product = ForeignKey(
        to=Product,
        on_delete=CASCADE,
        related_name="product_stores",
    )
    store = ForeignKey(
        to=Store,
        on_delete=CASCADE,
        related_name="store_products",
    )
    in_stock = IntegerField()
    price = DecimalField(
        max_digits=MAX_PRICE_DIGITS,
        decimal_places=MAX_DECIMAL_PLACES,
    )

    class Meta:
        """Meta class."""

        ordering = ("-created_at",)
        constraints = [
            UniqueConstraint(
                fields=["product", "store"],
                name="unique_product_per_store",
            )
        ]

    def clean(self):
        """Validate the model."""
        super().clean()
        if not self.quantity or self.quantity < 0:
            raise ValidationError("Quantity cannot be negative")
        if not self.price or self.price < self.MIN_PRICE:
            raise ValidationError("Price cannot be negative")

    def save(self, *args, **kwargs):
        """Override save to call full_clean."""
        self.full_clean()
        super().save(*args, **kwargs)
