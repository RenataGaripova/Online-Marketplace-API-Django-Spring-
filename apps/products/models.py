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
    Model,
    UniqueConstraint,
)
from django.contrib.auth import get_user_model

# Project modules
from apps.abstracts.models import AbstractBaseModel


class Category(AbstractBaseModel):
    """
    Category database (table) model.
    """
    MAX_NAME_LENGTH = 100

    name = CharField(max_length=MAX_NAME_LENGTH)
    description = TextField(blank=True, null=True)

    def __str__(self) -> str:
        """Returns the string representation of the object."""
        return self.name


class Product(AbstractBaseModel):
    """
    Product database (table) model.
    """
    MAX_NAME_LENGTH = 100
    MAX_PRICE_DIGITS = 10
    MAX_DECIMAL_PLACES = 2

    category = ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products')
    # seller = models.ForeignKey(
    #     settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = CharField(max_length=MAX_NAME_LENGTH)
    description = TextField(blank=True, null=True)
    price = DecimalField(
        max_digits=MAX_PRICE_DIGITS,
        decimal_places=MAX_DECIMAL_PLACES
    )
    image = ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self) -> str:
        """Returns the string representation of the object."""
        return self.name


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

    class Meta:
        """Meta class."""

        ordering = ('-created_at',)

    def __str__(self) -> str:
        """Magic str method."""
        return f'Store: {self.name}. Owner: {self.owner}.'


class StoreProductRelation(Model):
    """Many to many relation table for products and Stores."""

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
    in_stock = IntegerField(
        verbose_name="In stock",
    )

    class Meta:
        """Meta class."""

        constraints = [
            UniqueConstraint(
                fields=["product", "store"],
                name="unique_product_per_store",
            )
        ]
