# Django modules
from rest_framework.viewsets import (
    ModelViewSet
)
from django.shortcuts import get_object_or_404
from django.db.models import QuerySet
from rest_framework.permissions import IsAuthenticatedOrReadOnly

# Project modeules
from apps.products.models import Product
from .models import Review, Order, OrderItem, CartItem
from .serializers import (
    ReviewSerializer,
)
from .permissions import IsAuthorOrReadOnly


class ReviewViewSet(ModelViewSet):
    """ViewSet for Review model."""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_product(self, product_id: int) -> Product:
        """Returns a product by id."""
        product = get_object_or_404(
            Product,
            id=product_id,
        )
        return product

    def get_queryset(self) -> QuerySet[Review]:
        """Get all reviews for the related product."""
        product = self.get_product(
            product_id=self.kwargs.get("product_id"),
        )

        return product.reviews.all()

    def perform_create(self, serializer):
        """Saves a new review with a current user as an author."""
        serializer.save(
            author=self.request.user,
            product=self.get_product(
                product_id=self.kwargs.get("product_id"),
            )
        )
