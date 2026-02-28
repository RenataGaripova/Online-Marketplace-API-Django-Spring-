from typing import Any

from django.contrib.auth import get_user_model

from rest_framework import generics, permissions

from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """API view for user registration."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserMeView(generics.RetrieveUpdateAPIView):
    """API view for retrieving and updating current user profile."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> Any:
        """Return the currently authenticated user."""
        return self.request.user
