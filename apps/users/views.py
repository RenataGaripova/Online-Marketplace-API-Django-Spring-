# Python modules
from typing import Any

# Django modules
from rest_framework.viewsets import ViewSet
from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework import generics, permissions
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
)
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated
)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.decorators import action

# Project modules
from .serializers import (
    UserCreateSerializer,
    UserBaseSerializer,
    UserDetailedSerializer,
    UserResetPasswordSerializer,
    AddressSerializer,
)
from .models import CustomUser, Address

# USERS


class CustomUserViewSet(ViewSet):
    """Viewset for handling user-related endpoints."""

    pagination_class = LimitOffsetPagination

    def get_permissions(self):
        """Returns a list of permissions for a specific method."""
        if self.action in ("create",):
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def create(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles POST requests to create a new user instance.

        Parameters:
            request: DRFRequest,
                The request object.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing info about created user.
        """
        serializer: UserCreateSerializer = UserCreateSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(
            data=serializer.data,
            status=HTTP_201_CREATED,
        )

    def list(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles GET requests to retireve a list of users.

        Parameters:
            request: DRFRequest,
                The request object.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing list of all active users.
        """

        users = CustomUser.objects.annotate(
            total_reviews=Count("reviews", distinct=True),
        ).order_by("date_joined", "id")
        paginator = self.pagination_class()

        page = paginator.paginate_queryset(users, request)

        serializer: UserBaseSerializer = UserBaseSerializer(
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
        Handles GET requests to a single user.

        Parameters:
            request: DRFRequest,
                The request object.
            pk: int,
                User's id.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing user's details.
        """
        try:
            user = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return DRFResponse(
                data={"detail": "User not found"},
                status=HTTP_404_NOT_FOUND,
            )
        serializer: UserBaseSerializer = UserBaseSerializer(
            user, many=False,
        )
        return DRFResponse(
            data=serializer.data,
            status=HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=("get",)
    )
    def me(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ):
        """
        Handles GET requests to a current user.

        Parameters:
            request: DRFRequest,
                The request object.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing details about a user,
                who sent the request.
        """

        user = CustomUser.objects.filter(
            pk=request.user.id,
        ).annotate(
            total_reviews=Count("reviews", distinct=True),
        ).prefetch_related("addresses").first()
        serializer: UserDetailedSerializer = UserDetailedSerializer(
            user,
            many=False,
        )
        return DRFResponse(
            data=serializer.data,
            status=HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=("post",)
    )
    def reset_password(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles POST requests to change user's password.

        Parameters:
            request: DRFRequest,
                The request object.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing status of the request.
        """

        serializer: UserResetPasswordSerializer = UserResetPasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(
            status=HTTP_200_OK,
        )

# ADDRESSES


class AddressViewSet(ViewSet):
    """Viewset for handling addresses-related endpoints."""

    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthenticated,)

    def create(
        self,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles POST requests to create a new address instance.

        Parameters:
            request: DRFRequest,
                The request object.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing info about created address.
        """
    