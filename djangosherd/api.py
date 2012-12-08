from django.db.models import Q
from djangosherd.models import SherdNote
from mediathread.api import UserResource, ClassLevelAuthentication
from mediathread_main import course_details
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource


class SherdNoteAuthorization(Authorization):

    def apply_limits(self, request, object_list, course=None):
        # HACK: Tastypie does not call apply_limits on m2m relationships
        # Asset is calling apply_limits manually + specifying its course
        if course is None:
            course = request.course
        elif not course.is_member(request.user):
            return SherdNote.objects.none()

        # only request user's global annotations
        object_list = object_list.filter(asset__course=course)
        object_list = object_list.exclude(~Q(author=request.user),
                                          range1__isnull=True)

        # apply per course limitations
        if (not course.is_faculty(request.user) and
                not course_details.all_selections_are_visible(course)):

            # the user or a faculty member must be the selection author
            authorized = list(course.faculty)
            authorized.append(request.user)
            object_list = object_list.filter(author__in=authorized)

        return object_list


class SherdNoteResource(ModelResource):
    author = fields.ForeignKey(UserResource, 'author', full=True)

    class Meta:
        queryset = SherdNote.objects.all().order_by("id")
        excludes = ['tags', 'body', 'added', 'modified',
                    'range1', 'range2', 'annotation_data']
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']

        # User is logged into some course
        authentication = ClassLevelAuthentication()

        # User is authorized to look at this particular SherdNote
        authorization = SherdNoteAuthorization()

    def dehydrate(self, bundle):
        bundle.data['asset_id'] = str(bundle.obj.asset.id)
        bundle.data['is_global_annotation'] = \
            str(bundle.obj.is_global_annotation())
        return bundle
