# Python modules
from typing import Any

# Django modules
from rest_framework.viewsets import (
    ModelViewSet,
    ViewSet,
)
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.shortcuts import get_object_or_404
from django.db.models import QuerySet, Count, Sum, F
from django.db import transaction
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAdminUser,
    IsAuthenticated,
)
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.exceptions import PermissionDenied
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_403_FORBIDDEN,
)
from rest_framework.pagination import PageNumberPagination

# Project modules
from apps.products.models import Product, StoreProductRelation
from .models import Review, Order, OrderItem, CartItem
from .serializers import (
    ReviewSerializer,
    CartItemBaseSerializer,
    CartItemCreateSerializer,
    CartItemUpdateSerializer,
    CustomUserCartSerializer,
    OrderListCreateSerializer,
    OrderCreate400Serializer,
    OrderCreate404Serializer,
    HTTP405MethodNotAllowedSerializer,
    HTTP403PermissionDeniedSerializer,
    ReviewCreate400Serializer,
    Review404Serializer,
    CartItemList403Serializer,
    CartItemRetrieve404Serializer,
    CartItemCreate400Serializer,
    CartItemPartialUpdate404Serializer,
    CartItemDestroy404Serializer,
    OrderListGet403Serializer,
    OrderListGet404Serializer,
)
from .permissions import IsOwnerOrReadOnly
from apps.users.models import CustomUser


# ----------------------------------------------
# REVIEWS
# 

class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_product(self, product_id: int) -> Product:
        return get_object_or_404(Product, id=product_id)

    def get_queryset(self) -> QuerySet[Review]:
        product = self.get_product(product_id=self.kwargs.get("product_id"))
        return product.reviews.all()

    @extend_schema(
        summary="Review create",
        request=ReviewSerializer,
        responses={
            HTTP_201_CREATED: ReviewSerializer,
            HTTP_400_BAD_REQUEST: ReviewCreate400Serializer,
            HTTP_404_NOT_FOUND: Review404Serializer,
            HTTP_403_FORBIDDEN: HTTP403PermissionDeniedSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: HTTP405MethodNotAllowedSerializer,
        }
    )
    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            product=self.get_product(self.kwargs.get("product_id")),
        )


# ----------------------------------------------
# CART ITEMS
# 

class CartItemViewSet(ViewSet):
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.action == "list":
            classes = [IsAdminUser]
        elif self.action in ["retrieve", "partial_update", "destroy"]:
            classes = [IsOwnerOrReadOnly]
        else:
            classes = [IsAuthenticated]
        return [cls() for cls in classes]

    @extend_schema(
        summary="Users list retrieve",
        responses={
            HTTP_200_OK: CustomUserCartSerializer,
            HTTP_403_FORBIDDEN: CartItemList403Serializer,
            HTTP_405_METHOD_NOT_ALLOWED: HTTP405MethodNotAllowedSerializer,
        }
    )
    def list(self, request: DRFRequest) -> DRFResponse:
        if not request.user.is_staff:
            raise PermissionDenied("You can't access cart items of other users.")

        users = CustomUser.objects.prefetch_related("cart_items").annotate(
            total_positions=Count("cart_items__id")
        )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(users, request)
        serializer = CustomUserCartSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        summary="Cart item retrieve",
        responses={
            HTTP_200_OK: CartItemBaseSerializer,
            HTTP_403_FORBIDDEN: HTTP403PermissionDeniedSerializer,
            HTTP_404_NOT_FOUND: CartItemRetrieve404Serializer,
            HTTP_405_METHOD_NOT_ALLOWED: HTTP405MethodNotAllowedSerializer,
        }
    )
    def retrieve(self, request: DRFRequest, user_id: int) -> DRFResponse:
        user = get_object_or_404(CustomUser, pk=user_id)

        if request.user != user and not request.user.is_staff:
            raise PermissionDenied("You can't access cart items of other users.")

        cart_items = CartItem.objects.filter(user=user).select_related("store_product")

        serializer = CartItemBaseSerializer(cart_items, many=True)

        return DRFResponse({
            "user": user.email,
            "cart_items": serializer.data,
            "total": sum(item["total_product_price"] for item in serializer.data),
        })

    @extend_schema(
        summary="Cart item create",
        request=CartItemCreateSerializer,
        responses={
            HTTP_201_CREATED: CartItemCreateSerializer,
            HTTP_400_BAD_REQUEST: CartItemCreate400Serializer,
            HTTP_403_FORBIDDEN: HTTP403PermissionDeniedSerializer,
            HTTP_404_NOT_FOUND: CartItemRetrieve404Serializer,
            HTTP_405_METHOD_NOT_ALLOWED: HTTP405MethodNotAllowedSerializer,
        }
    )
    def create(self, request: DRFRequest) -> DRFResponse:
        store_product_id = request.data.get("store_product")
        quantity = request.data.get("quantity", 1)

        if not store_product_id:
            return DRFResponse({"product": ["Product can not be null."]}, HTTP_400_BAD_REQUEST)

        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return DRFResponse({"quantity": ["Quantity must be a valid integer."]}, HTTP_400_BAD_REQUEST)

        store_product = get_object_or_404(StoreProductRelation, id=store_product_id)

        if quantity > store_product.quantity:
            return DRFResponse(
                {"products": [f"Only {store_product.quantity} items are in stock."]},
                HTTP_400_BAD_REQUEST
            )

        existing = CartItem.objects.filter(user=request.user, store_product=store_product).first()

        if existing:
            existing.quantity += quantity
            existing.save()
            serializer = CartItemCreateSerializer(existing)
        else:
            serializer = CartItemCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)

        return DRFResponse(serializer.data, HTTP_201_CREATED)

    @extend_schema(
        summary="Cart item update",
        request=CartItemUpdateSerializer,
        responses={
            HTTP_200_OK: CartItemUpdateSerializer,
            HTTP_400_BAD_REQUEST: CartItemCreate400Serializer,
            HTTP_403_FORBIDDEN: HTTP403PermissionDeniedSerializer,
            HTTP_404_NOT_FOUND: CartItemPartialUpdate404Serializer,
            HTTP_405_METHOD_NOT_ALLOWED: HTTP405MethodNotAllowedSerializer,
        }
    )
    def partial_update(self, request: DRFRequest, pk: int) -> DRFResponse:
        item = CartItem.objects.filter(id=pk).select_related("store_product").first()
        if not item:
            return DRFResponse({"pk": [f"CartItem with id={pk} does not exist."]}, HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, item)

        quantity = request.data.get("quantity")
        if quantity is None:
            return DRFResponse({"quantity": ["Quantity is required"]}, HTTP_400_BAD_REQUEST)

        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return DRFResponse({"quantity": ["Quantity must be a valid integer."]}, HTTP_400_BAD_REQUEST)

        if quantity > item.store_product.quantity:
            return DRFResponse(
                {"products": [f"Only {item.store_product.quantity} items are in stock."]},
                HTTP_400_BAD_REQUEST
            )

        serializer = CartItemUpdateSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return DRFResponse(serializer.data)

    @extend_schema(
        summary="Cart item delete",
        responses={
            HTTP_204_NO_CONTENT: None,
            HTTP_403_FORBIDDEN: HTTP403PermissionDeniedSerializer,
            HTTP_404_NOT_FOUND: CartItemDestroy404Serializer,
            HTTP_405_METHOD_NOT_ALLOWED: HTTP405MethodNotAllowedSerializer,
        }
    )
    def destroy(self, request: DRFRequest, pk: int) -> DRFResponse:
        try:
            item = CartItem.objects.get(pk=pk)
        except CartItem.DoesNotExist:
            return DRFResponse({"pk": [f"CartItem with id={pk} does not exist."]}, HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, item)
        item.delete()
        return DRFResponse(status=HTTP_204_NO_CONTENT)


# ----------------------------------------------
# ORDERS LIST
#

class OrderListView(ListAPIView):
    serializer_class = OrderListCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = get_object_or_404(CustomUser, pk=self.kwargs.get("user_id"))
        return Order.objects.filter(user=user).prefetch_related("order_items").annotate(
            total_positions=Count("order_items__id"),
            total_price=Sum(F("order_items__price") * F("order_items__quantity")),
        )

    @extend_schema(
        summary="Order list retrieve",
        responses={
            HTTP_200_OK: OrderListCreateSerializer,
            HTTP_403_FORBIDDEN: OrderListGet403Serializer,
            HTTP_404_NOT_FOUND: OrderListGet404Serializer,
            HTTP_405_METHOD_NOT_ALLOWED: HTTP405MethodNotAllowedSerializer,
        }
    )
    def get(self, request: DRFRequest, *args, **kwargs):
        if request.user.id != self.kwargs.get("user_id") and not request.user.is_staff:
            raise PermissionDenied("You can't access orders of other users.")
        return super().get(request, *args, **kwargs)


# ----------------------------------------------
# ORDER CREATE
#

class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Order create",
        request=OrderListCreateSerializer,
        responses={
            HTTP_201_CREATED: OrderListCreateSerializer,
            HTTP_400_BAD_REQUEST: OrderCreate400Serializer,
            HTTP_404_NOT_FOUND: OrderCreate404Serializer,
            HTTP_403_FORBIDDEN: HTTP403PermissionDeniedSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: HTTP405MethodNotAllowedSerializer,
        }
    )
    def post(self, request: DRFRequest):
        with transaction.atomic():
            user = request.user
            cart_items = CartItem.objects.filter(user=user).select_related("store_product")

            if not cart_items.exists():
                return DRFResponse(
                    {"cart_items": ["Your cart is empty."]},
                    HTTP_400_BAD_REQUEST,
                )

            phone = request.data.get("phone_number")
            address = request.data.get("delivery_address")

            if not phone or not address:
                return DRFResponse({
                    "phone_number": ["Phone number can't be null."],
                    "delivery_address": ["Delivery address can't be null."]
                }, HTTP_400_BAD_REQUEST)

            order = Order.objects.create(
                user=user,
                phone_number=phone,
                delivery_address=address,
                status="P",
            )

            order_items = []
            total_price = 0
            total_positions = 0

            for item in cart_items:
                sp = item.store_product

                if sp.quantity < item.quantity:
                    continue

                name = sp.product.name
                price = sp.product.price

                order_items.append(OrderItem(
                    order=order,
                    store_product=sp,
                    name=name,
                    price=price,
                    quantity=item.quantity,
                ))

                total_price += round(price * item.quantity, 2)
                total_positions += item.quantity

                sp.quantity -= item.quantity
                sp.save()

            OrderItem.objects.bulk_create(order_items)
            cart_items.delete()

            serializer = OrderListCreateSerializer(
                order,
                context={"total_price": total_price, "total_positions": total_positions},
            )

            return DRFResponse(serializer.data, HTTP_201_CREATED)
