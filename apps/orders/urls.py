# Django modules
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Project modules
from apps.orders.views.cart_items import CartItemViewSet
from apps.orders.views.reviews import ReviewViewSet
from apps.orders.views.orders import OrderViewSet


v1_router: DefaultRouter = DefaultRouter()

v1_router.register(prefix="reviews", viewset=ReviewViewSet, basename="reviews")
v1_router.register(prefix="orders", viewset=OrderViewSet, basename="orders")

carts_list: CartItemViewSet = CartItemViewSet.as_view({
    "get": "list_all_carts",
    "post": "create",
})
users_cart: CartItemViewSet = CartItemViewSet.as_view({"get": "retrieve"})
cart_item_update: CartItemViewSet = CartItemViewSet.as_view({
    "patch": "partial_update",
    "delete": "destroy",
})

urlpatterns = [
    # router
    path("", include(v1_router.urls)),
    # carts
    path("users/carts/", carts_list, name="cartitem-list"),
    path("users/<int:pk>/cart/", users_cart, name="cartitem-user-cart"),
    path("users/carts/<int:pk>/", cart_item_update, name="cartitem-detail"),
]
