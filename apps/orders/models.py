# Python modules
from typing import Any

# Django modules
from django.db.models import (
    CharField,
    TextField,
    QuerySet,
    CASCADE,
    SET_NULL,
    ForeignKey,
    IntegerField,
    DecimalField,
    PositiveSmallIntegerField,
    PositiveIntegerField,
    PROTECT,
    Manager,
)
from django.contrib.auth import get_user_model
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator
)
from django.core.exceptions import ValidationError

# Project modules
from apps.products.models import Product, StoreProductRelation
from apps.abstracts.models import AbstractBaseModel, SoftDeleteQuerySet


class CartItemQuerySet(SoftDeleteQuerySet):
    """Cart Item QuerySet."""

    def cart_total_price(self) -> float:
        """Get total price of user's cart items."""
        if self:
            return sum(cart_item.get_products_price() for cart_item in self)
        return 0.0

    def cart_total_quantity(self) -> float:
        """Get total quantity of items in the user's cart."""
        if self:
            return sum(cart_item.quantity for cart_item in self)
        return 0.0


class CartItemManager(Manager.from_queryset(CartItemQuerySet)):
    """Cart Item Manager with soft delete filtering."""

    def get_queryset(
        self, *args: tuple[Any, ...],
        **kwargs: dict[Any, Any]
    ) -> QuerySet["CartItem"]:
        """Filter out soft-deleted objects."""
        return super().get_queryset().filter(
            deleted_at__isnull=True,
        )


class CartItem(AbstractBaseModel):
    """
    Cart item database (table) model.
    """

    user = ForeignKey(
        to=get_user_model(),
        on_delete=CASCADE,
    )
    store_product = ForeignKey(
        to=StoreProductRelation,
        on_delete=PROTECT,
    )
    quantity = PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )

    objects = CartItemManager()
    all_objects = Manager()

    class Meta:
        """Metadata."""

        default_related_name = "cart_items"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        """Magic method."""
        return f"{self.user.username}'s cart"

    def clean(self):
        """Validate the model."""
        super().clean()
        if not self.quantity or self.quantity < 1:
            raise ValidationError("Quantity cannot be negative")

    def save(self, *args, **kwargs):
        """Override save to call full_clean."""
        self.full_clean()
        super().save(*args, **kwargs)


class Order(AbstractBaseModel):
    """
    Order item database (table) model.
    """
    MAX_PHONE_NUMBER_LENGTH = 20
    MAX_STATUS_LENGTH = 20
    MAX_ADDRESS_LENGTH = 1024
    STATUS_CHOICES = [
        ('P', 'Processing'),
        ('S', 'Shipped'),
        ('D', 'Delivered'),
    ]

    user = ForeignKey(
        to=get_user_model(),
        on_delete=SET_NULL,
        null=True,
        blank=True,
    )
    phone_number = CharField(
        max_length=MAX_PHONE_NUMBER_LENGTH,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: "
                "'+999999999'. Up to 15 digits allowed."
            )
        ],
    )
    delivery_address = CharField(
        max_length=MAX_ADDRESS_LENGTH,
    )
    status = CharField(
        max_length=MAX_STATUS_LENGTH,
        choices=STATUS_CHOICES,
        default='P',
    )

    objects = CartItemManager()
    all_objects = Manager()

    class Meta:
        """Meta class."""

        default_related_name = "orders"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        """Magic str method."""
        return (f"Order № {self.pk}"
                f" User: {self.user.username}")

    def clean(self) -> None:
        """Validate the model."""
        super().clean()
        if self.phone_number:
            if not self.phone_number.startswith('+'):
                raise ValidationError("Phone number must start with +")
            digits = self.phone_number[1:]
            if not digits.isdigit():
                raise ValidationError(
                    "Phone number must contain only digits after +")
            if len(digits) < 9 or len(digits) > 15:
                raise ValidationError(
                    "Phone number must have between 9 and 15 digits")

        if not self.delivery_address or not self.delivery_address.strip():
            raise ValidationError("Delivery address cannot be empty")

    def save(self, *args, **kwargs) -> None:
        """Override save to call full_clean."""
        self.full_clean()
        super().save(*args, **kwargs)


class OrderItem(AbstractBaseModel):
    """
    Order item database (table) model.
    """

    MAX_ORDER_ITEM_NAME_LENGTH = 256
    MAX_PRICE_DIGITS = 10
    MAX_DECIMAL_PLACES = 2
    MIN_PRICE = 0.1

    order = ForeignKey(
        to=Order,
        on_delete=CASCADE,
    )
    store_product = ForeignKey(
        to=StoreProductRelation,
        on_delete=PROTECT,
    )
    name = CharField(
        max_length=MAX_ORDER_ITEM_NAME_LENGTH,
    )
    price = DecimalField(
        max_digits=MAX_PRICE_DIGITS,
        decimal_places=MAX_DECIMAL_PLACES,
    )
    quantity = PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        """Meta class."""

        ordering = ("-created_at",)
        default_related_name = "order_items"

    def __str__(self) -> str:
        """Magic str method."""
        return f"Order Item from order: {self.order.id}"

    def clean(self):
        """Validate the model."""
        super().clean()
        if not self.quantity or self.quantity < 1:
            raise ValidationError("Quantity cannot be negative")
        if not self.price or self.price < self.MIN_PRICE:
            raise ValidationError("Price cannot be so small")

    def save(self, *args, **kwargs):
        """Override save to call full_clean."""
        self.full_clean()
        super().save(*args, **kwargs)


class Review(AbstractBaseModel):
    """
    Review database (table) model.
    """
    MIN_RATE = 0
    MAX_RATE = 5

    product = ForeignKey(
        to=Product,
        on_delete=SET_NULL,
        null=True,
        blank=True,
    )
    user = ForeignKey(
        to=get_user_model(),
        on_delete=CASCADE,
    )
    rate = IntegerField(
        validators=(
            MinValueValidator(MIN_RATE),
            MaxValueValidator(MAX_RATE)
        ),
        default=0,
    )
    text = TextField()

    class Meta:
        """Meta class."""

        default_related_name = 'reviews'
        ordering = ('-created_at',)

    def __str__(self) -> str:
        """Magic str method."""
        return f'Comment from author {self.user.username}'

    def clean(self) -> None:
        """Validate the model."""
        super().clean()
        if not self.text or not self.text.strip():
            raise ValidationError("Review text cannot be empty")

    def save(self, *args, **kwargs) -> None:
        """Override save to call full_clean."""
        self.full_clean()
        super().save(*args, **kwargs)
