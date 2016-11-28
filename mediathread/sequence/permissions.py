from django.core.exceptions import PermissionDenied
from rest_framework import permissions


class SingleAuthorPermission(permissions.BasePermission):
    message = 'You can only update your own assets.'

    def has_permission(self, request, view):
        if view.kwargs.get('pk'):
            sa = view.get_object()
            if sa.author != request.user:
                raise PermissionDenied

        return True
