# Python modules
from typing import Type

# Django modules
from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    CharField,
    IntegerField,
)

# Project modules
from .models import Category, Product


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields: str = "__all__"


class CategoryBaseSerializer(ModelSerializer):
    """Category serializer."""

    class Meta:
        """Metadata."""

        model: Type[Category] = Category
        fields: tuple[str, str] = (
            "name",
            "description",
        )


class CategoryWithProductsSerializer(ModelSerializer):
    """Category with products serializer."""

    products: ProductSerializer = ProductSerializer(many=True)

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
