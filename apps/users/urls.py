# Django modules
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from rest_framework.routers import DefaultRouter

# Project modules
from .views import CustomUserViewSet

v1_router = DefaultRouter()
v1_router.register("users", CustomUserViewSet, basename="users")


urlpatterns = [
    path(
        'auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'
    ),
    path(
        'auth/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),
    path(
        'auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'
    ),
    path(
        'auth/', include(v1_router.urls),
    ),
]
