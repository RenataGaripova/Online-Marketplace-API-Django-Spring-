# Django modules
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
)

# Project modules
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["categories"],
        summary="List categories",
        description="Retrieve a list of all available categories.",
        responses={200: CategorySerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=["categories"],
        summary="Retrieve a category",
        description="Retrieve a single category by its ID.",
        responses={200: CategorySerializer},
    ),
    create=extend_schema(
        tags=["categories"],
        summary="Create a category",
        description="Create a new category.",
        request=CategorySerializer,
        responses={201: CategorySerializer},
    ),
    update=extend_schema(
        tags=["categories"],
        summary="Update a category",
        description="Fully update a category by its ID.",
        request=CategorySerializer,
        responses={200: CategorySerializer},
    ),
    partial_update=extend_schema(
        tags=["categories"],
        summary="Partially update a category",
        description="Partially update a category by its ID.",
        request=CategorySerializer,
        responses={200: CategorySerializer},
    ),
    destroy=extend_schema(
        tags=["categories"],
        summary="Delete a category",
        description="Delete a category by its ID.",
        responses={204: None},
    ),
)
class CategoryViewSet(viewsets.ModelViewSet):
    """
    Handles all types of requests related to categories models.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


@extend_schema_view(
    list=extend_schema(
        tags=["products"],
        summary="List products",
        description=(
            "Retrieve a list of products. "
            "Supports filtering by category "
            "and searching by name or description."
        ),
        parameters=[
            OpenApiParameter(
                name="category",
                type=int,
                description="Filter products by category ID.",
                required=False,
            ),
            OpenApiParameter(
                name="search",
                type=str,
                description="Search products by name or description.",
                required=False,
            ),
        ],
        responses={200: ProductSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=["products"],
        summary="Retrieve a product",
        description="Retrieve a single product by its ID.",
        responses={200: ProductSerializer},
    ),
    create=extend_schema(
        tags=["products"],
        summary="Create a product",
        description="Create a new product. Authentication is required.",
        request=ProductSerializer,
        responses={201: ProductSerializer},
    ),
    update=extend_schema(
        tags=["products"],
        summary="Update a product",
        description=(
            "Fully update a product by its ID."
            " Authentication is required."
        ),
        request=ProductSerializer,
        responses={200: ProductSerializer},
    ),
    partial_update=extend_schema(
        tags=["products"],
        summary="Partially update a product",
        description=(
            "Partially update a product by its ID."
            " Authentication is required."
        ),
        request=ProductSerializer,
        responses={200: ProductSerializer},
    ),
    destroy=extend_schema(
        tags=["products"],
        summary="Delete a product",
        description=(
            "Delete a product by its ID. "
            "Authentication is required."
        ),
        responses={204: None},
    ),
)
class ProductViewSet(viewsets.ModelViewSet):
    """
    Handles all types of requests related to products model.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)
