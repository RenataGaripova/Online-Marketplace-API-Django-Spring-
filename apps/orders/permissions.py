# Django modules
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    message = "Only Author can modify his reviews."

    def has_object_permission(self, request, view, obj):
        """Checks object permission."""

        if request.method in SAFE_METHODS:
            return True
        return request.user == obj.author
