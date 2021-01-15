from django.core.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from mediathread.main.course_details import (
    all_items_are_visible, cached_course_is_faculty,
    cached_course_is_member
)


class AssetIsVisible(BasePermission):
    message = 'You can only update assets visible to you.'

    def has_object_permission(self, request, view, obj):
        # Am I the owner of this asset?
        if obj.author == request.user:
            return True

        # Am I a faculty member?
        if cached_course_is_faculty(obj.course, request.user):
            return True

        # Does a faculty member own this item?
        if cached_course_is_faculty(obj.course, obj.author):
            return True

        # Has the faculty member restricted the item view?
        if not all_items_are_visible(obj.course):
            raise PermissionDenied

        return True


class AssetInMyCourse(BasePermission):
    message = 'You can only update assets in your courses.'

    def has_object_permission(self, request, view, obj):
        if not cached_course_is_member(obj.course, request.user):
            raise PermissionDenied

        return True
