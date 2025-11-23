# Python modules + Third party modules

# Django modules
from django.db.models import (
    CharField,
    TextField,
    QuerySet,
    CASCADE,
    SET_DEFAULT,
    ForeignKey,
    IntegerField,
    DecimalField,
    PositiveSmallIntegerField,
    PositiveIntegerField,
)
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.core.validators import MaxValueValidator, MinValueValidator

# Project modules
from apps.products.models import Product
from apps.abstracts.models import AbstractBaseModel


class CartItemQuerySet(QuerySet):
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


class CartItem(AbstractBaseModel):
    """
    Cart item database (table) model.
    """

    user = ForeignKey(
        to=get_user_model(),
        on_delete=CASCADE,
        blank=True,
        null=True,
        verbose_name="User",
    )
    product = ForeignKey(
        to=Product,
        on_delete=CASCADE,
        verbose_name="Related product"
    )
    quantity = PositiveSmallIntegerField(default=0, verbose_name="Quantity")

    objects = CartItemQuerySet().as_manager()

    class Meta:
        """Meta class."""

        ordering = ("-created_at",)

    def __str__(self) -> str:
        """Magic method."""
        return f"{self.user.username}'s cart"

    def get_products_price(self) -> float:
        """Get the subtotal of a cart."""
        return round(self.product.price * self.quantity, 2)


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
        on_delete=CASCADE,
        blank=True,
        null=True,
        verbose_name="User",
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
        verbose_name="Phone number"
    )
    delivery_address = CharField(
        max_length=MAX_ADDRESS_LENGTH,
        verbose_name="Delivery address"
    )
    status = CharField(
        max_length=MAX_STATUS_LENGTH,
        choices=STATUS_CHOICES,
        default='P',
        verbose_name="Order's status",
    )

    class Meta:
        """Meta class."""

        ordering = ("-created_at",)

    def __str__(self) -> str:
        """Magic str method."""
        return (f"Order № {self.pk}"
                f" User: {self.user.username}")


class OrderItem(AbstractBaseModel):
    """
    Order item database (table) model.
    """

    MAX_ORDER_ITEM_NAME_LENGTH = 256
    MAX_PRICE_DIGITS = 10
    MAX_DECIMAL_PLACES = 2

    order = ForeignKey(
        to=Order,
        on_delete=CASCADE,
        verbose_name="Order",
    )
    product = ForeignKey(
        to=Product,
        on_delete=CASCADE,
        verbose_name="Related product",
    )
    name = CharField(
        max_length=MAX_ORDER_ITEM_NAME_LENGTH,
        verbose_name="Products name",
    )
    price = DecimalField(
        max_digits=MAX_PRICE_DIGITS,
        decimal_places=MAX_DECIMAL_PLACES,
        verbose_name="Price",
    )
    quantity = PositiveIntegerField(
        default=0,
        verbose_name="Ordered quantity",
    )

    class Meta:
        """Meta class."""

        ordering = ("-created_at",)

    def __str__(self) -> str:
        """Magic str method."""
        return f"Order Item from order: {self.order.id}"


class Review(AbstractBaseModel):
    """
    Review database (table) model.
    """
    MIN_RATE = 0
    MAX_RATE = 5

    product = ForeignKey(
        to=Product,
        on_delete=CASCADE,
        verbose_name="Related product",
    )
    author = ForeignKey(
        to=get_user_model(),
        on_delete=SET_DEFAULT,
        default="Deleted Accounts",
        verbose_name="Author",
    )
    rate = IntegerField(
        validators=(
            MinValueValidator(MIN_RATE),
            MaxValueValidator(MAX_RATE)
        ),
        default=0,
        verbose_name='Rating',
    )
    text = TextField(verbose_name="Reviews's text")

    class Meta:
        """Meta class."""

        default_related_name = 'reviews'
        ordering = ('-created_at',)

    def __str__(self) -> str:
        """Magic str method."""
        return f'Comment from author {self.author.username}'
