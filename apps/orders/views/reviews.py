# Python modules
from typing import Any, Type, Optional

# DRF modules
from rest_framework.viewsets import (
    ViewSet,
)
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
)
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_401_UNAUTHORIZED,
    HTTP_400_BAD_REQUEST,
    HTTP_429_TOO_MANY_REQUESTS,
)

# Django modules
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

# Project modules
from apps.abstracts.decorators import obtain_object_by_pk
from apps.abstracts.mixins import DRFResponseMixin
from apps.abstracts.serializers import ErrorDetailSerializer
from apps.core.permissions import IsOwnerOrReadOnly
from apps.orders.models import Review
from apps.orders.serializers import (
    ReviewCreate400Serializer,
    ReviewSerializer,
)


class ReviewViewSet(DRFResponseMixin, ViewSet):
    """ViewSet that handles reviews-related requests."""

    queryset: QuerySet[Review] = Review.objects
    pagination_class: Type[PageNumberPagination] = PageNumberPagination
    permission_classes: tuple[
        Type[IsAuthenticatedOrReadOnly], Type[IsOwnerOrReadOnly]
    ] = (
        IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    )

    @extend_schema(
        summary="Get review's details.",
        tags=["reviews"],
        request=ReviewSerializer,
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
    @obtain_object_by_pk(
        queryset=queryset,
        class_name=Review,
        entity_name=_("Review"),
    )
    def retrieve(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles GET requests to a single review.

        Parameters:
            request: DRFRequest,
                The request object.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing review's details.
        """
        review: Review = kwargs.get("object")
        return self.get_drf_response(
            request=request,
            data=review,
            serializer_class=ReviewSerializer,
            many=False,
        )

    @extend_schema(
        summary="Review partial update.",
        tags=["reviews"],
        request=ReviewSerializer,
        responses={
            HTTP_200_OK: ReviewSerializer,
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
                description="Access forbidden.",
                response=ErrorDetailSerializer,
            ),
        },
    )
    @obtain_object_by_pk(
        queryset=queryset,
        class_name=Review,
        entity_name=_("Review"),
    )
    def partial_update(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles PATCH requests to a single review.

        Parameters:
            request: DRFRequest,
                The request object.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing updated review's details.
        """
        review: Optional[Review] = kwargs.get("object")
        self.check_object_permissions(request=request, obj=review)
        serializer: ReviewSerializer = ReviewSerializer(
            instance=review,
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
        summary="Review destroy.",
        tags=["reviews"],
        responses={
            HTTP_204_NO_CONTENT: {},
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
                description="Access forbidden.",
                response=ErrorDetailSerializer,
            ),
        },
    )
    @obtain_object_by_pk(
        queryset=queryset,
        class_name=Review,
        entity_name=_("Review"),
    )
    def destroy(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles DELETE requests to destroy an existing review.

        Parameters:
            request: DRFRequest,
                The request object.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A NO CONTENT response.
        """
        review: Review = kwargs.get("object")
        self.check_object_permissions(request=request, obj=review)
        review.delete()
        return DRFResponse(
            status=HTTP_204_NO_CONTENT,
        )
