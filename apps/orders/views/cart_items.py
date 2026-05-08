# Python modules
from typing import Any, Optional, Type

# DRF modules
from rest_framework.viewsets import (
    ViewSet,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
)
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_401_UNAUTHORIZED,
    HTTP_400_BAD_REQUEST,
    HTTP_429_TOO_MANY_REQUESTS,
)
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
)
from rest_framework.decorators import action

# Django modules
from django.db.models import QuerySet
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

# Project modules
from apps.users.models import CustomUser
from apps.abstracts.mixins import DRFResponseMixin
from apps.abstracts.serializers import ErrorDetailSerializer
from apps.abstracts.decorators import obtain_object_by_pk
from apps.core.permissions import IsOwnerOrReadOnly
from apps.orders.serializers import (
    UsernameLimit,
    CartItemBaseSerializer,
    CartItemCreateSerializer,
    CartItemUpdateSerializer,
    CustomUserCartSerializer,
    CartItemCreate400Serializer,
    CartItemUpdateDestroy404Serializer,
    CartItemRetrieveSerializer,
)
from apps.orders.models import CartItem


class CartItemViewSet(DRFResponseMixin, ViewSet):
    """Viewset for handling CartItem related endpoints."""

    pagination_class = PageNumberPagination
    permission_classes: tuple[
        Type[IsAuthenticated], Type[IsOwnerOrReadOnly]
    ] = (
        IsAuthenticated,
        IsOwnerOrReadOnly,
    )

    @extend_schema(
        summary="Get a list of cart items.",
        tags=["carts"],
        parameters=[
            OpenApiParameter("username", str, required=False),
            OpenApiParameter("limit", int, required=False),
        ],
        responses={
            HTTP_200_OK: CustomUserCartSerializer,
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
        detail=False,
        methods=("GET",),
        permission_classes=(IsAdminUser),
        url_name="list-all-carts",
        url_path="list-all-carts",
    )
    def list_all_carts(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles GET requests to list of cart items.

        Parameters:
            request: DRFRequest,
                The request object.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing a list of all users cart items.
        """
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

        if username:
            users: QuerySet[CustomUser] = (
                CustomUser.objects
                .get(username__icontains=username)
                .prefetch_related("cart_items")
                .annotate(total_positions=Count("cart_items__id"))
            )
        else:
            users: QuerySet[CustomUser] = CustomUser.objects.prefetch_related(
                "cart_items"
            ).annotate(total_positions=Count("cart_items__id"))

        return self.get_drf_response(
            request=request,
            data=users,
            serializer_class=CustomUserCartSerializer,
            many=True,
            paginator=self.pagination_class(),
            limit=limit,
        )

    @extend_schema(
        summary="Get cart items of a single user.",
        tags=["carts"],
        responses={
            HTTP_200_OK: CartItemRetrieveSerializer,
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
        queryset=CustomUser.objects,
        class_name=CustomUser,
        entity_name=_("User"),
    )
    def retrieve(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles GET requests to cart items of a single user.

        Parameters:
            request: DRFRequest
                The request object.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing list of specified user's cart items.
        """

        user: CustomUser = kwargs.get("object")

        # Check if the request was sent by staff or cart's owner:
        if request.user != user and not request.user.is_staff:
            raise PermissionDenied(
                "You can't access cart items of other users."
            )

        cart_items: QuerySet[CartItem] = CartItem.objects.filter(
            user=user,
        ).select_related("store_product")

        serializer: CartItemBaseSerializer = CartItemBaseSerializer(
            cart_items,
            many=True,
        )
        data: dict[str, dict[str, Any] | float | str] = {}
        data["user"] = user.email
        data["cart_items"] = serializer.data
        data["total"] = sum(
            (item["total_product_price"] for item in serializer.data)
        )
        return DRFResponse(data=data, status=HTTP_200_OK)

    @extend_schema(
        summary="Cart item create.",
        tags=["carts"],
        request=CartItemCreateSerializer,
        responses={
            HTTP_201_CREATED: CartItemCreateSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Bad request due to invalid input data.",
                response=CartItemCreate400Serializer,
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
    def create(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles POST requests to add a new item to user's cart.

        Parameters:
            request: DRFRequest,
                The request object.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing information about added cart item.
        """
        serializer: CartItemCreateSerializer = CartItemCreateSerializer(
            data=request.data,
            context={"user": request.user},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @extend_schema(
        summary="Cart item partial update.",
        tags=["carts"],
        request=CartItemUpdateSerializer,
        responses={
            HTTP_200_OK: CartItemUpdateSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Bad request due to invalid input data.",
                response=CartItemCreate400Serializer,
            ),
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Requested data was not found.",
                response=CartItemUpdateDestroy404Serializer,
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
        queryset=CartItem.objects.select_related("store_product"),
        class_name=CartItem,
        entity_name=_("Cart item"),
    )
    def partial_update(
        self,
        request: DRFRequest,
        pk: int,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles PATCH requests to partially update info
        about existing item in a cart.

        Parameters:
            request: DRFRequest,
                The request object.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing info about an updated item.
        """
        existing_cartitem: CartItem = kwargs.get("object")

        self.check_object_permissions(request=request, obj=existing_cartitem)

        serializer: CartItemUpdateSerializer = CartItemUpdateSerializer(
            instance=existing_cartitem,
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
        summary="Cart item destroy.",
        tags=["carts"],
        responses={
            HTTP_204_NO_CONTENT: {},
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Requested data was not found.",
                response=CartItemUpdateDestroy404Serializer,
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
        queryset=CartItem.objects,
        class_name=CartItem,
        entity_name=_("Cart item"),
    )
    def destroy(
        self,
        request: DRFRequest,
        pk: int,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles DELETE requests to cart items.

        Parameters:
            request: DRFRequest,
                The request object.
            pk: int,
                Cart item id.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                Status of the response.
        """
        existing_cartitem: CartItem = kwargs.get("object")
        self.check_object_permissions(request=request, obj=existing_cartitem)
        existing_cartitem.delete()
        return DRFResponse(
            status=HTTP_204_NO_CONTENT,
        )
