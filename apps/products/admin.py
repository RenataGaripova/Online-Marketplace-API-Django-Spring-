# Django modules
from django.contrib import admin

# Project modules
from .models import Category, Product, Store


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Category admin configuration class.
    """

    list_display = (
        "id",
        "name",
        "name_ru",
        "name_kz",
        "description",
        "description_ru",
        "description_kz",
        "created_at",
        "updated_at",
        "deleted_at",
    )
    search_fields = ("name",)
    list_filter = ("name",)
    fieldsets = [
        (
            "Category Information",
            {
                "fields": (
                    "name",
                    "name_ru",
                    "name_kz",
                    "description",
                    "description_ru",
                    "description_kz",
                ),
            },
        ),
    ]
    readonly_fields = (
        "created_at",
        "updated_at",
        "deleted_at",
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Product admin configuration class.
    """

    list_display = (
        "id",
        "name",
        "name_ru",
        "name_kz",
        "category",
        "description",
        "description_ru",
        "description_kz",
        "price",
        "created_at",
        "updated_at",
        "deleted_at",
    )
    search_fields = (
        "name",
        "category__name",
    )
    list_filter = (
        "category",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)

    fieldsets = [
        (
            "Product Information",
            {
                "fields": (
                    "name",
                    "name_ru",
                    "name_kz",
                    "description",
                    "description_ru",
                    "description_kz",
                    "price",
                    "image",
                ),
            },
        ),
        (
            "Relations",
            {
                "fields": (
                    "category",
                    # "seller",
                ),
            },
        ),
        (
            "Date-Time Information",
            {
                "fields": [
                    "created_at",
                    "updated_at",
                    "deleted_at",
                ],
            },
        ),
    ]

    readonly_fields = (
        "created_at",
        "updated_at",
        "deleted_at",
    )


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    """
    Review admin configuration class.
    """

    list_display = (
        "id",
        "owner",
        "name",
        "created_at",
        "updated_at",
        "deleted_at",
    )
    search_fields = ("owner__email", "name")
    list_filter = (
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)
    fieldsets = [
        (
            "Store Information",
            {
                "fields": ["owner", "name", "description"],
            },
        ),
        (
            "Date-Time Information",
            {
                "fields": [
                    "created_at",
                    "updated_at",
                    "deleted_at",
                ],
            },
        ),
    ]
    readonly_fields = (
        "created_at",
        "updated_at",
        "deleted_at",
    )
