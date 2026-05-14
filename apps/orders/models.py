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
from django.utils.translation import gettext_lazy as _

# Project modules
from apps.products.models import Product, StoreProductRelation
from apps.abstracts.models import AbstractBaseModel
from apps.users.models import Address


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
        verbose_name=_("User"),
    )
    store_product: ForeignKey = ForeignKey(
        to=StoreProductRelation,
        on_delete=PROTECT,
        verbose_name=_("Product"),
    )
    quantity: PositiveSmallIntegerField = PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name=_("Quantity"),
    )

    objects: Manager = CartItemManager()
    all_objects: Manager = Manager()

    class Meta:
        """Meta class."""

        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")
        ordering: tuple[str, str] = ("-created_at",)
        default_related_name: str = "cart_items"

    def __str__(self) -> str:
        """Magic method."""
        return f"Cart Item #{self.id}"


class Order(AbstractBaseModel):
    """
    Order item database (table) model.
    """

    MAX_PHONE_NUMBER_LENGTH: int = 20
    MAX_STATUS_LENGTH: int = 20
    MAX_ADDRESS_LENGTH: int = 1024
    STATUS_CHOICES: list[tuple[str, str]] = [
        ("P", _("Processing")),
        ("S", _("Shipped")),
        ("D", _("Delivered")),
    ]

    user: ForeignKey = ForeignKey(
        to=get_user_model(),
        on_delete=PROTECT,
        verbose_name=_("User"),
    )
    phone_number: CharField = CharField(
        max_length=MAX_PHONE_NUMBER_LENGTH,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message=_(
                    "Phone number must be entered in the format: "
                    "'+999999999'. Up to 15 digits allowed."
                ),
            )
        ],
        verbose_name=_("Phone number"),
    )
    delivery_address: ForeignKey = ForeignKey(
        to=Address,
        on_delete=PROTECT,
        blank=True,
        null=True,
        verbose_name=_("Address"),
    )
    status: CharField = CharField(
        max_length=MAX_STATUS_LENGTH,
        choices=STATUS_CHOICES,
        default="P",
        verbose_name=_("Order's status"),
    )

    class Meta:
        """Meta class."""

        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
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

    def save(self, *args, **kwargs) -> None:
        """Override save to call full_clean."""
        self.full_clean()
        super().save(*args, **kwargs)


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
        verbose_name=_("Order"),
    )
    store_product: ForeignKey = ForeignKey(
        to=StoreProductRelation,
        on_delete=PROTECT,
        verbose_name=_("Product"),
    )
    name: CharField = CharField(
        max_length=MAX_ORDER_ITEM_NAME_LENGTH,
        verbose_name=_("Products name"),
    )
    price: DecimalField = DecimalField(
        max_digits=MAX_PRICE_DIGITS,
        decimal_places=MAX_DECIMAL_PLACES,
        verbose_name=_("Price"),
    )
    quantity: PositiveIntegerField = PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name=_("Ordered quantity"),
    )

    class Meta:
        """Meta class."""

        ordering = ("-created_at",)
        default_related_name = "order_items"

    def __str__(self) -> str:
        """Magic str method."""
        return f"Order Item from order: {self.order.id}"


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
        verbose_name=_("Related product"),
    )
    user: ForeignKey = ForeignKey(
        to=get_user_model(),
        on_delete=CASCADE,
        verbose_name=_("Author"),
    )
    rate: IntegerField = IntegerField(
        validators=(MinValueValidator(MIN_RATE), MaxValueValidator(MAX_RATE)),
        default=0,
        verbose_name=_("Rating"),
    )
    text: TextField = TextField(verbose_name=_("Reviews's text"))

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
