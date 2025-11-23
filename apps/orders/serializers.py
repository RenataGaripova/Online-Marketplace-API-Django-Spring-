# Django modules
from rest_framework.serializers import (
    ModelSerializer,
    StringRelatedField,
)


# Project modules
from .models import (
    Order,
    OrderItem,
    CartItem,
    Review,
)


class ReviewSerializer(ModelSerializer):
    """Serializer for review model."""

    author = StringRelatedField()

    class Meta:
        """Metadata."""

        model = Review
        fields = ["id", "author", "rate", "text"]
        read_only_fields = ["author"]
