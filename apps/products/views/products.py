# Python modules
from typing import Any, Optional, Type

# Django modules
from django.db.models import QuerySet

# DRF modules
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_403_FORBIDDEN,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
)
from rest_framework.decorators import action
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
)

from apps.abstracts.decorators import obtain_object_by_pk
from apps.orders.models import Review
from apps.orders.serializers import (
    ReviewCreate400Serializer,
    ReviewSerializer,
    UsernameLimit,
)

# Project modules
from apps.abstracts.mixins import DRFResponseMixin
from apps.products.serializers import (
    ProductSerializer,
)
from apps.products.models import Product
from apps.abstracts.serializers import ErrorDetailSerializer


class ProductViewSet(DRFResponseMixin, ViewSet):
    """ViewSet for handling products-related endpoints."""

    permission_classes = (IsAuthenticated,)
    pagination_class: Type[PageNumberPagination] = PageNumberPagination

    @extend_schema(
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
        responses={
            HTTP_200_OK: ProductSerializer(many=True),
            HTTP_429_TOO_MANY_REQUESTS: OpenApiResponse(
                description="Too many requests",
                response=ErrorDetailSerializer,
            ),
        },
    )
    @action(
        methods=("get",),
        detail=False,
        url_path="list",
    )
    def list_products(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:

        products: QuerySet = Product.objects.all()

        category_id: Optional[str] = request.query_params.get("category")
        if category_id:
            products = products.filter(category_id=category_id)

        search: Optional[str] = request.query_params.get("search")
        if search:
            products = products.filter(
                name__icontains=search
            ) | products.filter(description__icontains=search)

        serializer: ProductSerializer = ProductSerializer(
            products,
            many=True,
        )
        return DRFResponse(
            data=serializer.data,
            status=HTTP_200_OK,
        )

    @extend_schema(
        tags=["products"],
        summary="Retrieve a product",
        description="Retrieve a single product by its ID.",
        responses={
            HTTP_200_OK: ProductSerializer,
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Product not found.",
                response=ErrorDetailSerializer,
            ),
        },
    )
    @action(
        methods=("get",),
        detail=True,
        url_path="retrieve",
    )
    def retrieve_product(
        self,
        request: DRFRequest,
        pk: int = None,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:

        product = Product.objects.filter(pk=pk).first()
        if not product:
            return DRFResponse(
                {"detail": "Not found"},
                status=HTTP_404_NOT_FOUND,
            )
        serializer: ProductSerializer = ProductSerializer(product)
        return DRFResponse(
            data=serializer.data,
            status=HTTP_200_OK,
        )

    @extend_schema(
        tags=["products"],
        summary="Create a product",
        description="Create a new product. Authentication is required.",
        request=ProductSerializer,
        responses={
            201: ProductSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: OpenApiResponse(
                description="Access forbidden.",
                response=ErrorDetailSerializer,
            ),
        },
    )
    @action(
        methods=("post",),
        detail=False,
        url_path="create",
    )
    def create_product(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:

        serializer: ProductSerializer = ProductSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(
            data=serializer.data,
            status=201,
        )

    @extend_schema(
        tags=["products"],
        summary="Update a product",
        description=(
            "Partially update a product by its ID. Authentication is required."
        ),
        request=ProductSerializer,
        responses={
            HTTP_200_OK: ProductSerializer,
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Product not found.",
                response=ErrorDetailSerializer,
            ),
        },
    )
    @action(
        methods=("patch",),
        detail=True,
        url_path="update",
    )
    def update_product(
        self,
        request: DRFRequest,
        pk: int = None,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:

        product = Product.objects.filter(pk=pk).first()
        if not product:
            return DRFResponse(
                {"detail": "Not found"},
                status=HTTP_404_NOT_FOUND,
            )
        serializer: ProductSerializer = ProductSerializer(
            product,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(
            data=serializer.data,
            status=HTTP_200_OK,
        )

    @extend_schema(
        tags=["products"],
        summary="Delete a product",
        description=(
            "Delete a product by its ID. Authentication is required."
        ),
        responses={
            HTTP_200_OK: OpenApiResponse(
                description="Product successfully deleted.",
            ),
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Product not found.",
                response=ErrorDetailSerializer,
            ),
        },
    )
    @action(
        methods=("delete",),
        detail=True,
        url_path="delete",
    )
    def delete_product(
        self,
        request: DRFRequest,
        pk: int = None,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:

        product = Product.objects.filter(pk=pk).first()
        if not product:
            return DRFResponse(
                {"detail": "Not found"},
                status=HTTP_404_NOT_FOUND,
            )
        product.delete()
        return DRFResponse(
            {"detail": "Deleted"},
            status=HTTP_200_OK,
        )

    @extend_schema(
        summary="Get a list of reviews.",
        tags=["reviews"],
        request=ReviewSerializer,
        parameters=[
            OpenApiParameter("username", str, required=False),
            OpenApiParameter("limit", int, required=False),
        ],
        responses={
            HTTP_200_OK: ReviewSerializer,
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Requested data was not found.",
                response=ErrorDetailSerializer,
            ),
            HTTP_403_FORBIDDEN: OpenApiResponse(
                description="Access forbidden.",
                response=ErrorDetailSerializer,
            ),
            HTTP_405_METHOD_NOT_ALLOWED: OpenApiResponse(
                description="Access forbidden.",
                response=ErrorDetailSerializer,
            ),
            HTTP_429_TOO_MANY_REQUESTS: OpenApiResponse(
                description="Server receives too many requests.",
                response=ErrorDetailSerializer,
            ),
        },
    )
    @action(
        detail=True,
        methods=("GET",),
        url_name="list_reviews",
        url_path="list-reviews",
    )
    @obtain_object_by_pk(
        queryset=Product.objects,
        class_name=Product,
        entity_name="Товар",
    )
    def list_reviews(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles GET requests to get a list of product's reviews.

        Parameters:
            request: DRFRequest,
                The request object.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing a list of reviews.
        """
        product: Optional[Product] = kwargs["object"]
        query_params_serializer: UsernameLimit = UsernameLimit(
            data=request.query_params,
        )

        query_params_serializer.is_valid(raise_exception=True)
        username: Optional[str] = query_params_serializer.validated_data.get(
            "username"
        )
        limit: Optional[int] = query_params_serializer.validated_data.get(
            "limit"
        )

        reviews: QuerySet[Review] = product.reviews.all()
        if username:
            reviews = reviews.select_related("user").filter(
                user__username__icontains=username
            )

        return self.get_drf_response(
            request=request,
            data=reviews,
            serializer_class=ReviewSerializer,
            many=True,
            paginator=self.pagination_class(),
            limit=limit,
        )

    @extend_schema(
        summary="Review create.",
        tags=["reviews"],
        request=ReviewSerializer,
        responses={
            HTTP_201_CREATED: ReviewSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Bad request due to invalid input data.",
                response=ReviewCreate400Serializer,
            ),
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Requested data was not found.",
                response=ErrorDetailSerializer,
            ),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description="User is not authorized.",
                response=ErrorDetailSerializer,
            ),
            HTTP_403_FORBIDDEN: OpenApiResponse(
                description="Access forbidden.",
                response=ErrorDetailSerializer,
            ),
            HTTP_405_METHOD_NOT_ALLOWED: OpenApiResponse(
                description="You don't have rights to perform this action.",
                response=ErrorDetailSerializer,
            ),
        },
    )
    @action(
        detail=True,
        methods=("POST",),
        url_name="post_review",
        url_path="post-review",
    )
    @obtain_object_by_pk(
        queryset=Product.objects,
        class_name=Product,
        entity_name="Товар",
    )
    def post_review(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles POST requests to create a new review.

        Parameters:
            request: DRFRequest,
                The request object.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing information about created review.
        """
        product: Product = kwargs.get("object")

        serializer: ReviewSerializer = ReviewSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user=request.user,
            product=product,
        )

        return DRFResponse(
            data=serializer.data,
            status=HTTP_201_CREATED,
        )
