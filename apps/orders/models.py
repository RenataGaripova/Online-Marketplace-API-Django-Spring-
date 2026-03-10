# Python modules + Third party modules

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
    RegexValidator,
)
from django.core.exceptions import ValidationError

# Project modules
from apps.products.models import Product, StoreProductRelation
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


class CartItemManager(Manager):
    """Cart Item Manager with soft delete filtering."""

    def get_queryset(self):
        """Filter out soft-deleted objects."""
        return CartItemQuerySet(self.model, using=self._db).filter(
            deleted_at__isnull=True,
        )


class CartItem(AbstractBaseModel):
    """
    Cart item database (table) model.
    """

    user: ForeignKey = ForeignKey(
        to=get_user_model(),
        on_delete=CASCADE,
        verbose_name="User",
    )
    store_product: ForeignKey = ForeignKey(
        to=StoreProductRelation,
        on_delete=PROTECT,
        verbose_name="Product",
    )
    quantity: PositiveSmallIntegerField = PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1)], verbose_name="Quantity"
    )

    objects: Manager = CartItemManager()
    all_objects: Manager = Manager()

    class Meta:
        """Meta class."""

        ordering: tuple[str, str] = ("-created_at",)
        default_related_name: str = "cart_items"

    def __str__(self) -> str:
        """Magic method."""
        return f"{self.user.username}'s cart"

    def delete(self, *args, **kwargs):
        """Override delete to perform soft delete."""
        self.soft_delete()


class Order(AbstractBaseModel):
    """
    Order item database (table) model.
    """

    MAX_PHONE_NUMBER_LENGTH: int = 20
    MAX_STATUS_LENGTH: int = 20
    MAX_ADDRESS_LENGTH: int = 1024
    STATUS_CHOICES: list[tuple[str, str]] = [
        ("P", "Processing"),
        ("S", "Shipped"),
        ("D", "Delivered"),
    ]

    user: ForeignKey = ForeignKey(
        to=get_user_model(),
        on_delete=SET_NULL,
        null=True,
        blank=True,
        verbose_name="User",
    )
    phone_number: CharField = CharField(
        max_length=MAX_PHONE_NUMBER_LENGTH,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message="Phone number must be entered in the format: "
                "'+999999999'. Up to 15 digits allowed.",
            )
        ],
        verbose_name="Phone number",
    )
    delivery_address: CharField = CharField(
        max_length=MAX_ADDRESS_LENGTH, verbose_name="Delivery address"
    )
    status: CharField = CharField(
        max_length=MAX_STATUS_LENGTH,
        choices=STATUS_CHOICES,
        default="P",
        verbose_name="Order's status",
    )

    class Meta:
        """Meta class."""

        ordering: tuple[str, str] = ("-created_at",)
        default_related_name: str = "orders"

    def __str__(self) -> str:
        """Magic str method."""
        return f"Order № {self.pk} User: {self.user.username}"

    def clean(self) -> None:
        """Validate the model."""
        super().clean()
        # Phone number validation
        if self.phone_number:
            if not self.phone_number.startswith("+"):
                raise ValidationError("Phone number must start with +")
            digits = self.phone_number[1:]
            if not digits.isdigit():
                raise ValidationError(
                    "Phone number must contain only digits after +"
                )
            if len(digits) < 9 or len(digits) > 15:
                raise ValidationError(
                    "Phone number must have between 9 and 15 digits"
                )

        # Delivery address validation
        if not self.delivery_address or not self.delivery_address.strip():
            raise ValidationError("Delivery address cannot be empty")

    def save(self, *args, **kwargs) -> None:
        """Override save to call full_clean."""
        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> None:
        """Override delete to perform soft delete."""
        self.soft_delete()


class OrderItem(AbstractBaseModel):
    """
    Order item database (table) model.
    """

    MAX_ORDER_ITEM_NAME_LENGTH: int = 256
    MAX_PRICE_DIGITS: int = 10
    MAX_DECIMAL_PLACES: int = 2

    order: ForeignKey = ForeignKey(
        to=Order,
        on_delete=CASCADE,
        verbose_name="Order",
    )
    store_product: ForeignKey = ForeignKey(
        to=StoreProductRelation,
        on_delete=PROTECT,
        verbose_name="Product",
    )
    name: CharField = CharField(
        max_length=MAX_ORDER_ITEM_NAME_LENGTH,
        verbose_name="Products name",
    )
    price: DecimalField = DecimalField(
        max_digits=MAX_PRICE_DIGITS,
        decimal_places=MAX_DECIMAL_PLACES,
        verbose_name="Price",
    )
    quantity: PositiveIntegerField = PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Ordered quantity",
    )

    class Meta:
        """Meta class."""

        ordering = ("-created_at",)
        default_related_name = "order_items"

    def __str__(self) -> str:
        """Magic str method."""
        return f"Order Item from order: {self.order.id}"

    def delete(self, *args, **kwargs) -> None:
        """Override delete to perform soft delete."""
        self.soft_delete()


class Review(AbstractBaseModel):
    """
    Review database (table) model.
    """

    MIN_RATE: int = 0
    MAX_RATE: int = 5

    product: ForeignKey = ForeignKey(
        to=Product,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        verbose_name="Related product",
    )
    user: ForeignKey = ForeignKey(
        to=get_user_model(),
        on_delete=CASCADE,
        verbose_name="Author",
    )
    rate: IntegerField = IntegerField(
        validators=(MinValueValidator(MIN_RATE), MaxValueValidator(MAX_RATE)),
        default=0,
        verbose_name="Rating",
    )
    text: TextField = TextField(verbose_name="Reviews's text")

    class Meta:
        """Meta class."""

        default_related_name = "reviews"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        """Magic str method."""
        return f"Comment from author {self.user.username}"

    def clean(self) -> None:
        """Validate the model."""
        super().clean()
        if not self.text or not self.text.strip():
            raise ValidationError("Review text cannot be empty")

    def save(self, *args, **kwargs) -> None:
        """Override save to call full_clean."""
        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> None:
        """Override delete to perform soft delete."""
        self.soft_delete()
