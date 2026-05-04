# Django modules
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Project modules
from apps.products.views.products import ProductViewSet
from apps.products.views.categories import CategoryViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="categories")
router.register(r"products", ProductViewSet, basename="product")

urlpatterns = [
    path("", include(router.urls)),
]
