# Django modules
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.views import APIView
from typing import Any


class IsOwnerOrReadOnly(BasePermission):
    """Permission class that allows only owners to modify their content."""

    message: str = "Only owner can modify his content."

    def has_object_permission(
        self, request: Request, view: APIView, obj: Any
    ) -> bool:
        """Check if user has permission to access the object."""
        if request.method in SAFE_METHODS:
            return True
        return request.user == obj.user
