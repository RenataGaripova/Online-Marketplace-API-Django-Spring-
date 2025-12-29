# Python modules
from typing import Any

# Django modules
from rest_framework.viewsets import (
    ViewSet,
)
from rest_framework.views import APIView
from rest_framework.generics import (
    ListAPIView,
)
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
    HTTP_403_FORBIDDEN,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_401_UNAUTHORIZED,
    HTTP_429_TOO_MANY_REQUESTS,
)
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter
)
# Project modules
from apps.products.models import Product, StoreProductRelation
from .models import Review, Order, OrderItem, CartItem
from .serializers import (
    ReviewSerializer,
    UsernameLimit,
    CartItemBaseSerializer,
    CartItemCreateSerializer,
    CartItemUpdateSerializer,
    CustomUserCartSerializer,
    OrderListCreateSerializer,
    ErrorDetailSerializer,
    ReviewCreate400Serializer,
    CartItemCreate400Serializer,
    CartItemUpdateDestroy404Serializer,
    CartItemRetrieveSerializer,
    OrderCreateOKSerializer,
    OrderCreate400Serializer,
    OrderCreate404Serializer,
)
from .permissions import IsOwnerOrReadOnly
from apps.users.models import CustomUser


# ----------------------------------------------
# REVIEWS
#

class ReviewAPIView(APIView):
    """
    Handles GET and POST requests to review model.
    """

    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)

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
        }
    )
    def get(
        self,
        request: DRFRequest,
        product_id: int,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles GET requests to get a list of product's reviews.

        Parameters:
            request: DRFRequest,
                The request object.
            product_id: int,
                Product's id.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing a list of reviews.
        """
        try:
            product: Product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return DRFResponse(
                data={
                    "detail": ["Product does not exist."],
                },
                status=HTTP_404_NOT_FOUND,
            )

        query_params_serializer: UsernameLimit = UsernameLimit(
            data=request.query_params,
        )

        query_params_serializer.is_valid(raise_exception=True)
        username = query_params_serializer.validated_data.get("username")
        limit = query_params_serializer.validated_data.get("limit")

        reviews: QuerySet[Review] = product.reviews.all()
        if username:
            reviews = reviews.select_related("user").filter(
                user__username__icontains=username)

        paginator: PageNumberPagination = self.pagination_class()
        paginator.page_size = limit
        page = paginator.paginate_queryset(reviews, request=request)

        serializer: ReviewSerializer = ReviewSerializer(
            page,
            many=True,
        )

        return paginator.get_paginated_response(serializer.data)

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
                description="Access forbidden.",
                response=ErrorDetailSerializer,
            ),
        }
    )
    def post(
        self,
        request: DRFRequest,
        product_id: int,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles POST requests to create a new review.

        Parameters:
            request: DRFRequest,
                The request object.
            product_id: int,
                Product's id.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing information about created review.
        """
        try:
            product: Product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return DRFResponse(
                data={
                    "detail": ["Product does not exist."],
                },
                status=HTTP_400_BAD_REQUEST,
            )

        serializer: ReviewSerializer = ReviewSerializer(
            data=request.data,
        )

        if not serializer.is_valid():
            return DRFResponse(
                data=serializer.errors,
                status=HTTP_400_BAD_REQUEST,
            )

        serializer.save(
            user=request.user,
            product=product,
        )

        return DRFResponse(
            data=serializer.data,
            status=HTTP_201_CREATED,
        )


class ReviewDetailAPIView(APIView):
    """
    Handles PATCH and DELETE requests to review model.
    """
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

    def get_object(
        self,
        product_id: int,
        pk: int,
    ) -> DRFResponse:
        """Retrieves a review by id."""
        review: Review = get_object_or_404(Review, pk=pk, product=product_id)
        return review

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
        }
    )
    def get(
        self,
        request: DRFRequest,
        product_id: int,
        pk: int,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles GET requests to a single review.

        Parameters:
            request: DRFRequest,
                The request object.
            product_id: int,
                Product's id.
            pk: int
                Review's id.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing review's details.
        """
        review: Review = self.get_object(
            product_id=product_id,
            pk=pk,
        )
        serializer: ReviewSerializer = ReviewSerializer(
            review,
            many=False,
        )
        return DRFResponse(
            data=serializer.data,
            status=HTTP_200_OK,
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
        }
    )
    def patch(
        self,
        request: DRFRequest,
        product_id: int,
        pk: int,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles PATCH requests to partially update an existing review.

        Parameters:
            request: DRFRequest,
                The request object.
            product_id: int,
                Product's id.
            pk: int,
                Review's id.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing an updated review.
        """
        review: Review = self.get_object(
            product_id=product_id,
            pk=pk,
        )
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
        }
    )
    def delete(
        self,
        request: DRFRequest,
        product_id: int,
        pk: int,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles DELETE requests to destroy an existing review.

        Parameters:
            request: DRFRequest,
                The request object.
            product_id: int,
                Product's id.
            pk: int,
                Review's id.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A NO CONTENT response.
        """
        review: Review = self.get_object(
            product_id=product_id,
            pk=pk,
        )
        self.check_object_permissions(request=request, obj=review)
        review.delete()
        return DRFResponse(
            status=HTTP_204_NO_CONTENT,
        )

# ----------------------------------------------
# CART ITEMS
#


class CartItemViewSet(ViewSet):
    """Viewset for handling CartItem related endpoints. """
    pagination_class = PageNumberPagination

    def get_permissions(self):
        """
        Instantiates and returns the
        list of permissions that this view requires.
        """
        if self.action == "list":
            permission_classes = [IsAdminUser]
        elif self.action in ["retrieve", "partial_update", "destroy"]:
            permission_classes = [IsOwnerOrReadOnly]
        elif self.action == "create":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

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
        }
    )
    def list(
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

        if not request.user.is_staff:
            raise PermissionDenied(
                "You can't access cart items of other users."
            )

        query_params_serializer: UsernameLimit = UsernameLimit(
            data=request.query_params,
        )

        query_params_serializer.is_valid(raise_exception=True)
        username = query_params_serializer.validated_data.get("username")
        limit = query_params_serializer.validated_data.get("limit")

        if username:
            users: QuerySet[CustomUser] = CustomUser.objects.get(
                username__icontains=username).prefetch_related(
                "cart_items").annotate(
                    total_positions=Count("cart_items__id")
            )
        else:
            users: QuerySet[CustomUser] = CustomUser.objects.prefetch_related(
                "cart_items").annotate(
                    total_positions=Count("cart_items__id")
            )

        paginator: PageNumberPagination = self.pagination_class()
        paginator.page_size = limit
        page = paginator.paginate_queryset(users, request=request)

        serializer: CustomUserCartSerializer = CustomUserCartSerializer(
            page,
            many=True,
        )

        return paginator.get_paginated_response(serializer.data)

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
        }
    )
    def retrieve(
        self,
        request: DRFRequest,
        user_id: int,
        *args: tuple[Any, ...],
        **kwargs: dict[Any, Any],
    ) -> DRFResponse:
        """
        Handles GET requests to cart items of a single user.

        Parameters:
            request: DRFRequest
                The request object.
            user_id: int,
                User's id.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing list of specified user's cart items.
        """

        user: CustomUser = get_object_or_404(CustomUser, pk=user_id)

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
        }
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

        store_product_id: int = request.data.get("store_product")
        quantity: int = int(request.data.get("quantity")) or 1

        if not store_product_id:
            return DRFResponse(
                data={
                    "detail": ["Product can not be null."],
                },
                status=HTTP_404_NOT_FOUND,
            )

        store_product: StoreProductRelation = get_object_or_404(
            StoreProductRelation,
            id=store_product_id,
        )

        if quantity > store_product.quantity:
            return DRFResponse(
                data={
                    "detail": [
                        f"Only {store_product.quantity} items are in stock."
                    ],
                },
                status=HTTP_400_BAD_REQUEST,
            )

        existing_cartitem: QuerySet[CartItem] = CartItem.objects.filter(
            user=request.user,
            store_product=store_product,
        ).first()

        if existing_cartitem:
            existing_cartitem.quantity += int(quantity)
            existing_cartitem.save()
            serializer: CartItemCreateSerializer = CartItemCreateSerializer(
                instance=existing_cartitem,
            )
        else:
            serializer: CartItemCreateSerializer = CartItemCreateSerializer(
                data=request.data,
            )
            if not serializer.is_valid():
                return DRFResponse(
                    data=serializer.errors,
                    status=HTTP_400_BAD_REQUEST,
                )
            serializer.save(
                user=request.user,
            )

        return DRFResponse(
            data=serializer.data,
            status=HTTP_201_CREATED,
        )

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
        }
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
            pk: int,
                Cart item id.
            *args: list,
                Additional positional arguments.
            **kwargs: dict,
                Additional keyword arguments.

        Returns:
            DRFResponse -
                A response containing info about an updated item.
        """
        try:
            existing_cartitem: CartItem = CartItem.objects.filter(
                id=pk).select_related("store_product").first()
        except CartItem.DoesNotExist:
            return DRFResponse(
                data={
                    "detail": [f"CartItem with id={pk} does not exist."]
                },
                status=HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(request=request, obj=existing_cartitem)

        quantity: int = int(request.data.get("quantity"))

        store_product: StoreProductRelation = existing_cartitem.store_product

        if quantity > store_product.quantity:
            return DRFResponse(
                data={
                    "products": [
                        f"Only {store_product.quantity} items are in stock."
                    ],
                },
                status=HTTP_400_BAD_REQUEST,
            )

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
        }
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
        try:
            existing_cartitem: CartItem = CartItem.objects.get(pk=pk)
        except CartItem.DoesNotExist:
            return DRFResponse(
                data={
                    "detail": [f"CartItem with id={pk} does not exist."]
                },
                status=HTTP_404_NOT_FOUND,
            )
        self.check_object_permissions(request=request, obj=existing_cartitem)
        existing_cartitem.delete()
        return DRFResponse(
            status=HTTP_204_NO_CONTENT,
        )

# ----------------------------------------------
# ORDERS
#


class OrderListView(ListAPIView):
    """
    Handles GET requests to Order model.
    """

    serializer_class = OrderListCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[Order]:
        """Get a list of user's orders."""
        user = get_object_or_404(CustomUser, pk=self.kwargs.get("user_id"))

        user_orders = Order.objects.filter(user=user).prefetch_related(
            "order_items").annotate(
                total_positions=Count("order_items__id"),
                total_price=Sum(
                    F("order_items__price") * F("order_items__quantity")
                ),
        )

        return user_orders

    @extend_schema(
        summary="Get a list of user orders.",
        tags=["orders"],
        responses={
            HTTP_200_OK: OrderListCreateSerializer,
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
        }
    )
    def get(
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

        if (
            request.user.id != self.kwargs.get("user_id") and
            not request.user.is_staff
        ):
            raise PermissionDenied("You can't access orders of other users.")

        return super().get(request, *args, **kwargs)


class OrderCreateView(APIView):
    """
    View to create a new order from existing cart items.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Create a new order.",
        tags=["orders"],
        request=OrderCreateOKSerializer,
        responses={
            HTTP_201_CREATED: OrderListCreateSerializer,
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
        }
    )
    def post(
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
            user = request.user
            cart_items = CartItem.objects.filter(
                user=user).select_related("store_product")

            if not cart_items.exists():
                return DRFResponse(
                    data={
                        "detail": ["Your cart is empty."],
                    },
                    status=HTTP_400_BAD_REQUEST,
                )

            phone_number: str = request.data.get("phone_number")
            delivery_address: str = request.data.get("delivery_address")
            status: str = "P"

            if not phone_number or not delivery_address:
                return DRFResponse(
                    data={
                        "phone_number": ["Phone number can't be null."],
                        "delivery_address": ["Delivery address can't be null."]
                    },
                    status=HTTP_404_NOT_FOUND,
                )

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
                total_positions += quantity

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

            serializer: OrderListCreateSerializer = OrderListCreateSerializer(
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
