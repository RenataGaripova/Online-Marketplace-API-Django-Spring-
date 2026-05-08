from typing import Any

# Django modules
from django.db import models
from django.db.models import (
    CharField,
    TextField,
    ManyToManyField,
    ImageField,
    CASCADE,
    ForeignKey,
    DecimalField,
    IntegerField,
    UniqueConstraint,
)
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

# Project modules
from apps.abstracts.models import AbstractBaseModel

# CATEGORY


class Category(AbstractBaseModel):
    """
    Category database (table) model.
    """

    MAX_NAME_LENGTH: int = 100

    name: CharField = CharField(
        max_length=MAX_NAME_LENGTH,
        unique=True,
        verbose_name=_("Name (English)"),
    )
    name_ru: CharField = CharField(
        max_length=MAX_NAME_LENGTH,
        unique=True,
        null=True,
        blank=True,
        verbose_name=_("Name (Russian)"),
    )
    name_kk: CharField = CharField(
        max_length=MAX_NAME_LENGTH,
        unique=True,
        null=True,
        blank=True,
        verbose_name=_("Name (Kazakh)"),
    )
    description: TextField = TextField(
        blank=True,
        null=True,
        verbose_name=_("Description (English)"),
    )
    description_ru: TextField = TextField(
        blank=True,
        null=True,
        verbose_name=_("Description (Russian)"),
    )
    description_kk: TextField = TextField(
        blank=True,
        null=True,
        verbose_name=_("Description (Kazakh)"),
    )

    class Meta:
        """Meta class."""

        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self) -> str:
        """Returns the string representation of the object."""
        return self.name


# PRODUCT


class StoreProductRelation(AbstractBaseModel):
    """Many to many relation table for products and Stores."""

    MAX_NAME_LENGTH: int = 100
    MAX_PRICE_DIGITS: int = 10
    MAX_DECIMAL_PLACES: int = 2

    product: ForeignKey = ForeignKey(
        to="Product",
        on_delete=CASCADE,
        verbose_name=_("Product"),
    )
    store: ForeignKey = ForeignKey(
        to="Store",
        on_delete=CASCADE,
        verbose_name=_("Store"),
    )
    quantity: IntegerField = IntegerField(
        verbose_name=_("In stock"),
    )
    price: DecimalField = DecimalField(
        max_digits=MAX_PRICE_DIGITS,
        decimal_places=MAX_DECIMAL_PLACES,
        verbose_name=_("Price"),
    )

    class Meta:
        """Meta class."""

        verbose_name = _("Store-Product")
        verbose_name_plural = _("Store-Products")
        constraints: list[Any, Any] = [
            UniqueConstraint(
                fields=["product", "store"],
                name="unique_product_per_store",
            )
        ]

    def clean(self) -> None:
        """Validate the model."""
        super().clean()
        if self.quantity is not None and self.quantity < 0:
            raise ValidationError("Quantity cannot be negative")
        if self.price is not None and self.price < 0:
            raise ValidationError("Price cannot be negative")

    def save(self, *args, **kwargs) -> None:
        """Override save to call full_clean."""
        self.full_clean()
        super().save(*args, **kwargs)


class Product(AbstractBaseModel):
    """
    Product database (table) model.
    """

    MAX_NAME_LENGTH: int = 100
    MAX_PRICE_DIGITS: int = 10
    MAX_DECIMAL_PLACES: int = 2
    MIN_PRICE: int = 0.01

    category: ForeignKey = ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name=_("Related category"),
    )
    name: CharField = CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name=_("Name (English)"),
    )
    name_ru: CharField = CharField(
        max_length=MAX_NAME_LENGTH,
        unique=True,
        null=True,
        blank=True,
        verbose_name=_("Name (Russian)"),
    )
    name_kk: CharField = CharField(
        max_length=MAX_NAME_LENGTH,
        unique=True,
        null=True,
        blank=True,
        verbose_name=_("Name (Kazakh)"),
    )
    description = TextField(
        blank=True,
        null=True,
        verbose_name=_("Description (English)"),
    )
    description_ru: TextField = TextField(
        blank=True,
        null=True,
        verbose_name=_("Description (Russian)"),
    )
    description_kk: TextField = TextField(
        blank=True,
        null=True,
        verbose_name=_("Description (Kazakh)"),
    )
    price: DecimalField = DecimalField(
        max_digits=MAX_PRICE_DIGITS,
        decimal_places=MAX_DECIMAL_PLACES,
        validators=[MinValueValidator(MIN_PRICE)],
        verbose_name=_("Price"),
    )
    image: ImageField = ImageField(
        upload_to="products/",
        blank=True,
        null=True,
        verbose_name=_("Image"),
    )

    class Meta:
        """Meta class."""

        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering: tuple[str, str] = ("-created_at",)

    def __str__(self) -> str:
        """Returns the string representation of the object."""
        return self.name


# STORE


class Store(AbstractBaseModel):
    """
    Store database (table) model.
    """

    MAX_STORE_NAME_LENGTH: int = 128

    owner: ForeignKey = ForeignKey(
        to=get_user_model(),
        on_delete=CASCADE,
        verbose_name=_("Owner"),
    )
    name: CharField = CharField(
        max_length=MAX_STORE_NAME_LENGTH,
        verbose_name=_("Store's name"),
    )
    description: TextField = TextField(
        verbose_name=_("Description (English)"),
    )
    description_ru: TextField = TextField(
        blank=True,
        null=True,
        verbose_name=_("Description (Russian)"),
    )
    description_kk: TextField = TextField(
        blank=True,
        null=True,
        verbose_name=_("Description (Kazakh)"),
    )
    products: ManyToManyField = ManyToManyField(
        to="Product",
        through=("StoreProductRelation"),
        related_name="stores",
        verbose_name=_("Available products"),
    )

    class Meta:
        """Meta class."""

        verbose_name = _("Store")
        verbose_name_plural = _("Stores")
        ordering: tuple[str, str] = ("-created_at",)

    def __str__(self) -> str:
        """Magic str method."""
        return self.name
