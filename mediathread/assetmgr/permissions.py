from django.core.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


class AssetIsOwnedByMe(BasePermission):
    message = 'You can only update assets owned to you.'

    def has_object_permission(self, request, view, obj):
        # Am I the owner of this asset?
        if obj.author == request.user:
            return True

        raise PermissionDenied
