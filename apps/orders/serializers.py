# Python modules
from typing import Any, Type

# Django modules
from rest_framework.serializers import (
    ModelSerializer,
    StringRelatedField,
    SerializerMethodField,
    IntegerField,
    DecimalField,
    Serializer,
    ListField,
    CharField,
)

# Project modules
from .models import (
    Order,
    OrderItem,
    CartItem,
    Review,
)
from apps.users.models import (
    CustomUser,
)

# ----------------------------------------------
# REVIEWS
#


class ReviewCreate400Serializer(Serializer):
    """
    Serializer for Review create 400 responses (validation errors).
    """

    product: ListField = ListField(child=CharField(), required=False)
    rate: ListField = ListField(child=CharField(), required=False)
    text: ListField = ListField(child=CharField(), required=False)

    class Meta:
        fields: tuple[str, str] = ("product", "rate", "text")


class ReviewSerializer(ModelSerializer):
    """Serializer for Review model."""

    user: StringRelatedField = StringRelatedField()

    class Meta:
        """Metadata."""

        model: Type[Review] = Review
        fields: tuple[str, str] = [
            "id",
            "user",
            "product",
            "rate",
            "text",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
        read_only_fields: tuple[str, str] = [
            "id",
            "user",
            "product",
            "created_at",
            "updated_at",
            "deleted_at",
        ]


class UsernameLimit(Serializer):
    """Serializer for query parameters."""

    username: CharField = CharField(
        required=False,
        allow_blank=True,
    )
    limit: IntegerField = IntegerField(
        required=False,
        min_value=1,
        max_value=25,
        default=25,
    )


# ----------------------------------------------
# CART ITEMS
#


class CartItemRetrieve404Serializer(Serializer):
    """
    Serializer for CartItem retrieve 404 responses (cart/user not found).
    """

    pk: ListField = ListField(child=CharField(), required=False)
    detail: CharField = CharField(required=False)

    class Meta:
        fields: tuple[str, str] = ("pk", "detail")


class CartItemCreate400Serializer(Serializer):
    """
    Serializer for CartItem create 400 responses.
    """

    product: ListField = ListField(child=CharField(), required=False)
    products: ListField = ListField(child=CharField(), required=False)
    store_product: ListField = ListField(child=CharField(), required=False)
    quantity: ListField = ListField(child=CharField(), required=False)

    class Meta:
        fields: tuple[str, str] = (
            "product",
            "products",
            "store_product",
            "quantity",
        )


class CartItemUpdateDestroy404Serializer(Serializer):
    """
    Serializer for partial_update 404 responses (CartItem not found).
    """

    pk: ListField = ListField(child=CharField())

    class Meta:
        fields: tuple[str, str] = ("pk",)


class CartItemBaseSerializer(ModelSerializer):
    """Serializer for CartItem model."""

    total_product_price: SerializerMethodField = SerializerMethodField(
        method_name="get_total_product_price"
    )

    class Meta:
        """Metadata."""

        model = CartItem
        fields: tuple[str, str] = (
            "id",
            "store_product",
            "quantity",
            "total_product_price",
            "created_at",
            "updated_at",
            "deleted_at",
        )
        read_only_fields: tuple[str, str] = [
            "id",
            "created_at",
            "updated_at",
            "deleted_at",
        ]

    def get_total_product_price(self, obj: CartItem) -> float:
        """Get total price for single position in a cart."""

        return round(obj.store_product.price * obj.quantity, 2)


class CartItemRetrieveSerializer(Serializer):
    """Serializer for retrieving cart items with user and total price."""

    MAX_PRICE_DIGITS: int = 10
    MAX_DECIMAL_PLACES: int = 2

    user: CharField = CharField()
    cart_items: CartItemBaseSerializer = CartItemBaseSerializer(many=True)
    total: DecimalField = DecimalField(
        max_digits=MAX_PRICE_DIGITS, decimal_places=MAX_DECIMAL_PLACES
    )


class CartItemCreateSerializer(CartItemBaseSerializer):
    """Serializer for CartItem model.
    Handles the creation of new cart item."""

    user: StringRelatedField = StringRelatedField()

    class Meta:
        """Metadata."""

        model: Type[CartItem] = CartItem
        fields: tuple[str, str] = (
            "id",
            "user",
            "store_product",
            "quantity",
            "total_product_price",
            "created_at",
            "updated_at",
            "deleted_at",
        )
        read_only_fields: tuple[str, str] = [
            "user",
            "id",
            "created_at",
            "updated_at",
            "deleted_at",
        ]


class CartItemUpdateSerializer(CartItemBaseSerializer):
    """
    Serializer for CartItem model.
    Handles the partial update of a cart item.
    """

    user: StringRelatedField = StringRelatedField()

    class Meta:
        """Metadata."""

        model: Type[CartItem] = CartItem
        fields: tuple[str, str] = (
            "id",
            "user",
            "store_product",
            "quantity",
            "total_product_price",
            "created_at",
            "updated_at",
            "deleted_at",
        )
        read_only_fields: tuple[str, str] = [
            "id",
            "user",
            "store_product",
            "created_at",
            "updated_at",
            "deleted_at",
        ]


class CustomUserCartSerializer(ModelSerializer):
    cart_items: CartItemBaseSerializer = CartItemBaseSerializer(many=True)
    total_positions: IntegerField = IntegerField()

    class Meta:
        """Metadata."""

        model: Type[CustomUser] = CustomUser
        fields: tuple[str, str] = (
            "id",
            "email",
            "total_positions",
            "cart_items",
        )


# ----------------------------------------------
# ORDERS
#


class OrderCreateOKSerializer(ModelSerializer):
    """Serializer for representing data for order creation."""

    class Meta:
        """Metadata."""

        model: Type[Order] = Order
        fields: CartItemBaseSerializer = (
            "phone_number",
            "delivery_address",
        )


class OrderCreate400Serializer(Serializer):
    """
    Serializer for unsuccessful order creation responses.
    """

    cart_items: ListField = ListField(child=CharField())

    class Meta:
        fields: CartItemBaseSerializer = ("cart_items",)


class OrderCreate404Serializer(Serializer):
    """
    Serializer for unsuccessful order creation responses.
    """

    phone_number: ListField = ListField(
        child=CharField(),
        required=False,
    )
    delivery_address: ListField = ListField(
        child=CharField(),
        required=False,
    )

    class Meta:
        """Customization of the Serializer metadata."""

        fields: tuple[str, str] = (
            "phone_number",
            "delivery_address",
        )


class OrderItemBaseSerializer(ModelSerializer):
    """Order Item Base Serializer."""

    total_product_price: SerializerMethodField = SerializerMethodField(
        method_name="get_total_product_price"
    )

    class Meta:
        """Metadata."""

        model: Type[OrderItem] = OrderItem
        fields: tuple[str, str] = (
            "id",
            "store_product",
            "name",
            "price",
            "quantity",
            "total_product_price",
        )

    def get_total_product_price(self, obj: OrderItem) -> float:
        """Get total price for single position in an order."""

        return round(obj.price * obj.quantity, 2)


class OrderListCreateSerializer(ModelSerializer):
    """Serializer for list of orders."""

    MAX_PRICE_DIGITS: int = 10
    MAX_DECIMAL_PLACES: int = 2

    user: StringRelatedField = StringRelatedField()
    order_items: OrderItemBaseSerializer = OrderItemBaseSerializer(many=True)
    total_positions: IntegerField = IntegerField(read_only=True)
    total_price: DecimalField = DecimalField(
        max_digits=MAX_PRICE_DIGITS,
        decimal_places=MAX_DECIMAL_PLACES,
        read_only=True,
    )

    class Meta:
        """Metadata."""

        model: Type[Order] = Order
        fields: tuple[str, str] = (
            "id",
            "user",
            "phone_number",
            "delivery_address",
            "status",
            "total_positions",
            "total_price",
            "order_items",
            "created_at",
            "updated_at",
            "deleted_at",
        )
        read_only_fields: tuple[str, str] = [
            "status",
            "created_at",
            "updated_at",
            "deleted_at",
        ]

    def to_representation(self, instance):
        data: dict[Any, Any] = super().to_representation(instance)
        data["total_positions"] = self.context.get("total_positions")
        data["total_price"] = self.context.get("total_price")
        return data
