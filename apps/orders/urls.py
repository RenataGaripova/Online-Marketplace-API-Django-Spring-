# Django modules
from django.urls import path
from rest_framework.routers import DefaultRouter

# Project modules
from .views import (
    ReviewAPIView,
    ReviewDetailAPIView,
    CartItemViewSet,
    OrderListView,
    OrderCreateView,
)

v1_router = DefaultRouter()
carts_list = CartItemViewSet.as_view({"get": "list", "post": "create"})
users_cart = CartItemViewSet.as_view({"get": "retrieve"})
cart_item_update = CartItemViewSet.as_view({
    "patch": "partial_update",
    "delete": "destroy",
})

urlpatterns = [
    path(
        "products/<int:product_id>/reviews/",
        ReviewAPIView.as_view(),
        name="review-list",
    ),
    path(
        "products/<int:product_id>/reviews/<int:pk>/",
        ReviewDetailAPIView.as_view(),
        name="review-detail",
    ),
    path("users/carts/", carts_list, name="cartitem-list"),
    path("users/<int:user_id>/cart/", users_cart, name="cartitem-user-cart"),
    path("users/carts/<int:pk>/", cart_item_update, name="cartitem-detail"),
    path(
        "users/<int:user_id>/orders/",
        OrderListView.as_view(),
        name="order-list",
    ),
    path(
        "users/<int:user_id>/order_create/",
        OrderCreateView.as_view(),
        name="order-create",
    ),
]
