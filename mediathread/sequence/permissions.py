from django.core.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnly(BasePermission):
    """Based on IsAuthenticatedOrReadOnly in rest_framework."""
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class SingleAuthor(BasePermission):
    message = 'You can only update your own assets.'

    def has_object_permission(self, request, view, obj):
        if request.method == 'PUT' and obj.author != request.user:
            raise PermissionDenied

        return True
