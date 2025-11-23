# Django modules
from django.contrib import admin

# Project modules
from .models import Order, OrderItem, CartItem, Review


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """
    Cart item admin configuration class.
    """

    list_display = (
        "id",
        "user",
        "product",
        "quantity",
        "created_at",
        "updated_at",
        "deleted_at",
    )
    search_fields = ("user__email", "product__name")
    list_filter = ("quantity",)
    ordering = ("-created_at",)
    fieldsets = [
        (
            "Cart Information",
            {
                "fields": ["user", "product", "quantity"],
            },
        ),
        (
            "Date-Time Information",
            {
                "fields": ["created_at", "updated_at", "deleted_at",],
            },
        ),
    ]
    readonly_fields = ("created_at",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Order item admin configuration class.
    """

    list_display = (
        "id",
        "order",
        "product",
        "name",
        "price",
        "quantity",
        "created_at",
        "updated_at",
        "deleted_at",
    )
    search_fields = ("order", "product", "name")
    list_filter = ("quantity", "price")
    ordering = ("-created_at",)
    fieldsets = [
        (
            "Order Information",
            {
                "fields": ["order"],
            },
        ),
        (
            "Product Information",
            {
                "fields": ["product", "name", "quantity", "price"],
            },
        ),
        (
            "Date-Time Information",
            {
                "fields": ["created_at", "updated_at", "deleted_at",],
            },
        ),
    ]
    readonly_fields = ("created_at",)


@admin.register(Order)
class Order(admin.ModelAdmin):
    """
    Order admin configuration class.
    """

    list_display = (
        "id",
        "user",
        "phone_number",
        "delivery_address",
        "status",
        "created_at",
        "updated_at",
        "deleted_at",
    )
    search_fields = (
        "user__email",
        "product__name",
        "user__phone",
        "delivery_address",
        "status",
    )
    list_filter = ("status", "created_at", "updated_at")
    ordering = ("-created_at",)
    fieldsets = [
        (
            "User Information",
            {
                "fields": ["user", "phone_number"],
            },
        ),
        (
            "Destination Information",
            {
                "fields": [
                    "delivery_address",
                ],
            },
        ),
        (
            "Status Information",
            {
                "fields": [
                    "status",
                ],
            },
        ),
        (
            "Date-Time Information",
            {
                "fields": ["created_at", "updated_at", "deleted_at",],
            },
        ),
    ]
    readonly_fields = ("created_at",)


@admin.register(Review)
class ReviewItemAdmin(admin.ModelAdmin):
    """
    Review admin configuration class.
    """

    list_display = (
        "id",
        "author",
        "product",
        "rate",
        "created_at",
        "updated_at",
        "deleted_at",
    )
    search_fields = ("author__username", "author__email", "product__name")
    list_filter = ("rate",)
    fieldsets = [
        (
            "Review Information",
            {
                "fields": ["author", "product", "rate", "text"],
            },
        ),
        (
            "Date-Time Information",
            {
                "fields": ["created_at", "updated_at", "deleted_at",],
            },
        ),
    ]
    readonly_fields = ("created_at",)
