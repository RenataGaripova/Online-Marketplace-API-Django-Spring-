# Python modules
from typing import Type

# Django modules
from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    CharField,
    IntegerField,
    SerializerMethodField,
)

# Project modules
from .models import Category, Product
from apps.abstracts.serializers import TimeZoneSerializerMixin


class ProductBaseSerializer(TimeZoneSerializerMixin, ModelSerializer):
    """Base serializer for product model."""

    name: SerializerMethodField = SerializerMethodField()
    description: SerializerMethodField = SerializerMethodField()

    class Meta:
        model = Product
        fields: str = "__all__"
        read_only_filed: tuple[str, ...] = (
            "id",
            "created_at",
            "updated_at",
            "deleted_at",
        )

    def get_name(self, obj: Product) -> str:
        lang = getattr(self.context.get("request"), "LANGUAGE_CODE", "en")
        return getattr(obj, f"name_{lang}", obj.name)

    def get_description(self, obj: Product) -> str:
        lang = getattr(self.context.get("request"), "LANGUAGE_CODE", "en")
        return getattr(obj, f"description_{lang}", obj.description)


class ProductReadSerializer(ProductBaseSerializer):
    """Serializer for reading a product."""

    pass


class ProductWriteSerializer(TimeZoneSerializerMixin, ModelSerializer):
    """Serializer for adding/updating a product."""

    class Meta:
        model = Product
        fields: str = "__all__"
        read_only_filed: tuple[str, ...] = (
            "id",
            "created_at",
            "updated_at",
            "deleted_at",
        )


class CategoryBaseSerializer(ModelSerializer):
    """Category serializer."""

    name: SerializerMethodField = SerializerMethodField()
    description: SerializerMethodField = SerializerMethodField()

    class Meta:
        """Metadata."""

        model: Type[Category] = Category
        fields: tuple[str, str] = (
            "name",
            "description",
        )

    def get_name(self, obj: Category) -> str:
        lang = getattr(self.context.get("request"), "LANGUAGE_CODE", "en")
        return getattr(obj, f"name_{lang}", obj.name)

    def get_description(self, obj: Category) -> str:
        lang = getattr(self.context.get("request"), "LANGUAGE_CODE", "en")
        return getattr(obj, f"description_{lang}", obj.description)


class CategoryWithProductsSerializer(CategoryBaseSerializer):
    """Category with products serializer."""

    products: ProductReadSerializer = ProductReadSerializer(many=True)

    class Meta:
        """Metadata."""

        model: Type[Category] = Category
        fields: tuple[str, ...] = (
            "name",
            "description",
            "products",
        )


class NameLimitSerializer(Serializer):
    """Serializer for 'name' query-param."""

    name = CharField(
        required=False,
        allow_blank=True,
    )
    limit = IntegerField(
        required=False,
        min_value=1,
        max_value=25,
        default=25,
    )
