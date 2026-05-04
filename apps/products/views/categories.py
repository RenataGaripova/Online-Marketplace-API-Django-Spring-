# Python modules
from typing import Any, Optional, List

# Django modules
from django.db.models import QuerySet, Manager

# DRF modules
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_429_TOO_MANY_REQUESTS,
)
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
)


# Project modules
from ..serializers import (
    NameLimitSerializer,
    CategoryBaseSerializer,
    CategoryWithProductsSerializer,
)
from ..models import Category
from apps.abstracts.serializers import ErrorDetailSerializer


class CategoryViewSet(ViewSet):
    """Viewset for handling category-related endpoints."""

    pagination_class = PageNumberPagination

    def get_permissions(self):
        """
        Instantiates and returns the
        list of permissions that this view requires.
        """
        if self.action in ("list", "retrieve"):
            permission_classes = [
                AllowAny,
            ]
        permission_classes = []
        return [permission() for permission in permission_classes]

    @extend_schema(
        summary="Get a list of categories.",
        tags=["categories"],
        parameters=[
            OpenApiParameter("name", str, required=False),
            OpenApiParameter("limit", int, required=False),
        ],
        responses={
            HTTP_200_OK: CategoryBaseSerializer,
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Requested data was not found.",
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
    def list(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles GET requests to list of categories.

        Parameters:
            request: DRFRequest,
                The request object.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing a list of all categories.
        """

        categories: Manager = Category.objects

        query_params_serializer: NameLimitSerializer = NameLimitSerializer(
            data=request.query_params,
        )

        query_params_serializer.is_valid(raise_exception=True)
        name: Optional[str] = query_params_serializer.validated_data.get(
            "name"
        )
        limit: Optional[int] = query_params_serializer.validated_data.get(
            "limit"
        )

        if name:
            categories: QuerySet[Category] = categories.filter(
                name__icontains=name
            )
        else:
            categories: QuerySet[Category] = categories.all()

        paginator: PageNumberPagination = self.pagination_class()
        paginator.page_size = limit
        page: Optional[List[Category]] = paginator.paginate_queryset(
            categories, request=request
        )

        serializer: CategoryBaseSerializer = CategoryBaseSerializer(
            page,
            many=True,
        )

        return paginator.get_paginated_response(serializer.data)

    def retrieve(
        self,
        request: DRFRequest,
        pk: int,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles GET requests to get info about 1 category.

        Parameters:
            request: DRFRequest,
                The request object.
            pk: int
                Unique id of a category.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing a info about some category.
        """

        category: Category = Category.objects.filter(id=pk).prefetch_related(
            "products"
        )
        category = category.first()
        serializer: CategoryWithProductsSerializer = (
            CategoryWithProductsSerializer(
                category,
            )
        )
        return DRFResponse(data=serializer.data, status=HTTP_200_OK)
