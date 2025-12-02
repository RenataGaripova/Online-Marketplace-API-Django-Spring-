# Django modules
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    message = "Only owner can modify his content."

    def has_object_permission(self, request, view, obj):
        """Checks object permission."""

        if request.method in SAFE_METHODS:
            return True
        return request.user == obj.user
    