# Python modules
from typing import Any, Type

# DRF modules
from rest_framework.viewsets import (
    ViewSet,
)
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.pagination import PageNumberPagination
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
)
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
)

# Django modules
from django.db.models import QuerySet, Count, Sum, F
from django.db import transaction

# Project modules
from apps.orders.serializers import (
    OrderCreate400Serializer,
    OrderCreate404Serializer,
    OrderCreateOKSerializer,
    OrderReadSerializer,
    OrderCreateSerializer,
)
from apps.products.models import StoreProductRelation
from apps.users.models import CustomUser
from apps.orders.models import CartItem, Order, OrderItem
from apps.abstracts.mixins import DRFResponseMixin
from apps.abstracts.serializers import ErrorDetailSerializer


class OrderViewSet(DRFResponseMixin, ViewSet):
    """Handles orders-related endpoints."""

    queryset: QuerySet[Order] = Order.objects
    pagination_class = PageNumberPagination
    permission_classes: tuple[Type[IsAuthenticated],] = (IsAuthenticated,)
    MAX_PAGE_SIZE: int = 10

    @extend_schema(
        summary="Get a list of your orders.",
        tags=["orders"],
        responses={
            HTTP_200_OK: OrderReadSerializer,
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
    def list(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles GET requests to a list of specified user's orders.

        Parameters:
            request: DRFRequest,
                The request object.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing a list of user's orders.
        """
        user_orders: QuerySet[Order] = (
            self.queryset
            .filter(user=request.user)
            .prefetch_related("order_items")
            .annotate(
                total_positions=Count("order_items__id"),
                total_price=Sum(
                    F("order_items__price") * F("order_items__quantity")
                ),
            )
        )
        return self.get_drf_response(
            request=request,
            data=user_orders,
            limit=self.MAX_PAGE_SIZE,
            serializer_class=OrderReadSerializer,
            paginator=self.pagination_class(),
            many=True,
        )

    @extend_schema(
        summary="Create a new order.",
        tags=["orders"],
        request=OrderCreateOKSerializer,
        responses={
            HTTP_201_CREATED: OrderCreateSerializer,
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Bad request due to invalid input data.",
                response=OrderCreate400Serializer,
            ),
            HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Requested data was not found.",
                response=OrderCreate404Serializer,
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
        Handles POST requests to create a new order from exisiting items.
        Order is done by the user sending the request.

        Parameters:
            request: DRFRequest,
                The request object.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing info about a new order.
        """
        with transaction.atomic():
            user: CustomUser = request.user
            cart_items: QuerySet[CartItem] = CartItem.objects.filter(
                user=user
            ).select_related("store_product")

            if not cart_items.exists():
                return DRFResponse(
                    data={
                        "detail": ["Your cart is empty."],
                    },
                    status=HTTP_400_BAD_REQUEST,
                )

            request_serializer: OrderCreateOKSerializer = (
                OrderCreateOKSerializer(data=request.data)
            )
            request_serializer.is_valid(raise_exception=True)

            phone_number: str = request_serializer.data.get("phone_number")
            delivery_address: str = request_serializer.data.get(
                "delivery_address"
            )
            status: str = "P"

            order: Order = Order.objects.create(
                user=request.user,
                phone_number=phone_number,
                delivery_address=delivery_address,
                status=status,
            )

            order_items: list[OrderItem] = []
            total_price: float = 0
            total_positions: int = 0

            for item in cart_items:
                store_product: StoreProductRelation = item.store_product

                if store_product.quantity < item.quantity:
                    continue

                store_product: StoreProductRelation = item.store_product
                name: str = store_product.product.name
                price: float = store_product.price
                quantity: int = item.quantity
                total_price += round(price * quantity, 2)
                total_positions += 1

                order_items.append(
                    OrderItem(
                        order=order,
                        store_product=store_product,
                        name=name,
                        price=price,
                        quantity=quantity,
                    )
                )

                store_product.quantity -= item.quantity
                store_product.save()

            OrderItem.objects.bulk_create(order_items)
            cart_items.delete()

            serializer: OrderCreateSerializer = OrderCreateSerializer(
                instance=order,
                context={
                    "total_price": total_price,
                    "total_positions": total_positions,
                },
            )

            return DRFResponse(
                data=serializer.data,
                status=HTTP_201_CREATED,
            )
