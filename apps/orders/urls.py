# Django modules
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Project modules
from .views import ReviewViewSet

v1_router = DefaultRouter()
v1_router.register(
    r'products/(?P<product_id>\d+)/reviews',
    ReviewViewSet,
    basename="reviews",
)

urlpatterns = [
    path("", include(v1_router.urls)),
]