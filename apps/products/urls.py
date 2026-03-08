# Django modules
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Project modules
from .views import CategoryViewSet, ProductViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="categories")
router.register(r"products", ProductViewSet, basename="product")

urlpatterns = [
    path("", include(router.urls)),
]
