from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet

v1_router: DefaultRouter = DefaultRouter()
v1_router.register("auths", CustomUserViewSet, basename="auths")

urlpatterns = [
    path("", include(v1_router.urls)),
    path(
        "auths/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "auths/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "auths/token/verify/", TokenVerifyView.as_view(), name="token_verify"
    ),
]
