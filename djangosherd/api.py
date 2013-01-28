from django.db.models import Q
from djangosherd.models import SherdNote
from mediathread.api import UserResource, ClassLevelAuthentication
from mediathread_main import course_details
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.resources import ModelResource


class SherdNoteAuthorization(Authorization):

    def apply_limits(self, request, object_list):
        # only request user's global annotations
        object_list = object_list.exclude(~Q(author=request.user),
                                          range1__isnull=True)

        # Make sure the requesting user is allowed to see this note
        invisible = []
        for note in object_list:
            course = note.asset.course

            if not course.is_member(request.user):
                invisible.append(note.id)
            elif (not course.is_faculty(request.user) and
                  not course_details.all_selections_are_visible(course)):
                # apply per course limitations
                # the user or a faculty member must be the selection author
                authorized = list(course.faculty)
                authorized.append(request.user)
                if not note.author in authorized:
                    invisible.append(note.id)

        object_list = object_list.exclude(id__in=invisible)
        return object_list.order_by('id')


class SherdNoteResource(ModelResource):
    author = fields.ForeignKey(UserResource, 'author', full=True)

    class Meta:
        queryset = SherdNote.objects.all().order_by("id")
        excludes = ['tags', 'body', 'added', 'modified',
                    'range1', 'range2', 'annotation_data']
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        filtering = {'author': ALL_WITH_RELATIONS}

        # User is logged into some course
        authentication = ClassLevelAuthentication()

        # User is authorized to look at this particular SherdNote
        authorization = SherdNoteAuthorization()

    def dehydrate(self, bundle):
        bundle.data['asset_id'] = str(bundle.obj.asset.id)
        bundle.data['is_global_annotation'] = \
            str(bundle.obj.is_global_annotation())
        return bundle
