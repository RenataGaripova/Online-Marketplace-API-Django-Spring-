# Python modules
from typing import Any

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
    BooleanField,
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

class OrderCreate400Serializer(Serializer):
    """
    Serializer for unsuccessful order creation responses.
    """
    cart_items = ListField(child=CharField())

    class Meta:
        fields = ("cart_items",)


class OrderCreate404Serializer(Serializer):
    """
    Serializer for unsuccessful order creation responses.
    """

    phone_number = ListField(
        child=CharField(),
        required=False,
    )
    delivery_address = ListField(
        child=CharField(),
        required=False,
    )

    class Meta:
        """Customization of the Serializer metadata."""

        fields = (
            "phone_number",
            "delivery_address",
            )


class HTTP405MethodNotAllowedSerializer(Serializer):
    """
    Serializer for HTTP 405 Method Not Allowed response.
    """

    detail = CharField()

    class Meta:
        """Customization of the Serializer metadata."""
        fileds = (
            "detail",
        )


class HTTP403PermissionDeniedSerializer(Serializer):
    """
    Serializer for HTTP 403 Permission Denied response.
    """

    detail = CharField()

    class Meta:
        fields = ("detail",)



class ReviewCreate400Serializer(Serializer):
    """
    Serializer for Review create 400 responses (validation errors).
    """

    product = ListField(child=CharField(), required=False)
    rate = ListField(child=CharField(), required=False)
    text = ListField(child=CharField(), required=False)

    class Meta:
        fields = ("product", "rate", "text")


class Review404Serializer(Serializer):
    """
    Serializer for Review related 404 responses (e.g., product not found).
    """

    detail = CharField()

    class Meta:
        fields = ("detail",)


class CartItemList403Serializer(Serializer):
    """
    Serializer for CartItem list 403 responses (permission denied).
    """

    detail = CharField()

    class Meta:
        fields = ("detail",)


class CartItemRetrieve404Serializer(Serializer):
    """
    Serializer for CartItem retrieve 404 responses (cart/user not found).
    """

    pk = ListField(child=CharField(), required=False)
    detail = CharField(required=False)

    class Meta:
        fields = ("pk", "detail")


class CartItemCreate400Serializer(Serializer):
    """
    Serializer for CartItem create 400 responses.
    """

    product = ListField(child=CharField(), required=False)
    products = ListField(child=CharField(), required=False)
    store_product = ListField(child=CharField(), required=False)
    quantity = ListField(child=CharField(), required=False)

    class Meta:
        fields = ("product", "products", "store_product", "quantity")


class CartItemPartialUpdate404Serializer(Serializer):
    """
    Serializer for partial_update 404 responses (CartItem not found).
    """

    pk = ListField(child=CharField())

    class Meta:
        fields = ("pk",)


class CartItemDestroy404Serializer(Serializer):
    """
    Serializer for destroy 404 responses (CartItem not found).
    """

    pk = ListField(child=CharField())

    class Meta:
        fields = ("pk",)


class OrderListGet403Serializer(Serializer):
    """
    Serializer for Order list 403 responses (permission denied).
    """

    detail = CharField()

    class Meta:
        fields = ("detail",)


class OrderListGet404Serializer(Serializer):
    """
    Serializer for Order list 404 responses (user not found).
    """
    
    detail = CharField()

    class Meta:
        fields = ("detail",)


class ReviewSerializer(ModelSerializer):
    """Serializer for Review model."""

    user = StringRelatedField()

    class Meta:
        """Metadata."""

        model = Review
        fields = ["id", "user", "rate", "text", "created_at", "updated_at"]
        read_only_fields = ["user", "created_at", "updated_at"]


class CartItemBaseSerializer(ModelSerializer):
    """Serializer for CartItem model."""

    total_product_price = SerializerMethodField(
        method_name="get_total_product_price"
    )

    class Meta:
        """Metadata."""

        model = CartItem
        fields = (
            "id",
            "store_product",
            "quantity",
            "total_product_price",
            "created_at",
            "updated_at",
        )
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_total_product_price(self, obj: CartItem) -> float:
        """Get total price for single position in a cart."""

        return round(obj.store_product.price * obj.quantity, 2)


class CartItemCreateSerializer(CartItemBaseSerializer):
    """Serializer for CartItem model.
    Handles the creation of new cart item."""

    user = StringRelatedField()

    class Meta:
        """Metadata."""
        model = CartItem
        fields = (
            "id",
            "user",
            "store_product",
            "quantity",
            "total_product_price",
            "created_at",
            "updated_at",
        )
        read_only_fields = ["user", "id", "created_at", "updated_at"]


class CartItemUpdateSerializer(CartItemBaseSerializer):
    """
    Serializer for CartItem model.
    Handles the partial update of a cart item.
    """
    user = StringRelatedField()

    class Meta:
        """Metadata."""
        model = CartItem
        fields = (
            "id",
            "user",
            "store_product",
            "quantity",
            "total_product_price",
            "created_at",
            "updated_at",
        )
        read_only_fields = [
            "id",
            "user",
            "store_product",
            "created_at",
            "updated_at"
        ]


class CustomUserCartSerializer(ModelSerializer):
    cart_items = CartItemBaseSerializer(many=True)
    total_positions = IntegerField()

    class Meta:
        """Metadata."""
        model = CustomUser
        fields = (
            "id",
            "email",
            "total_positions",
            "cart_items",
        )


class OrderItemBaseSerializer(ModelSerializer):
    """Order Item Base Serializer."""

    total_product_price = SerializerMethodField(
        method_name="get_total_product_price"
    )

    class Meta:
        """Metadata."""

        model = OrderItem
        fields = (
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
    MAX_PRICE_DIGITS = 10
    MAX_DECIMAL_PLACES = 2

    user = StringRelatedField()
    order_items = OrderItemBaseSerializer(many=True)
    total_positions = IntegerField(read_only=True)
    total_price = DecimalField(
        max_digits=MAX_PRICE_DIGITS,
        decimal_places=MAX_DECIMAL_PLACES,
        read_only=True,
    )

    class Meta:
        """Metadata."""
        model = Order
        fields = (
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
        )
        read_only_fields = ["status", "created_at", "updated_at"]

    def to_representation(self, instance):
        data: dict[Any, Any] = super().to_representation(instance)
        data["total_positions"] = self.context.get("total_positions")
        data["total_price"] = self.context.get("total_price")
        return data
