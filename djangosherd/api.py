from tastypie import fields
from tastypie.resources import ModelResource
from mediathread.api import ClassLevelAuthentication, UserResource
from tastypie.authorization import Authorization
from djangosherd.models import SherdNote
from mediathread_main import course_details


class SherdNoteAuthorization(Authorization):
    '''
    Authorization answers the question "Is permission granted for this user
    to take this action?" This usually involves checking permissions such as
    Create/Read/Update/Delete access, or putting limits
    on what data the user can access.
    '''
    def is_authorized(self, request, object=None):
        if not object:
            # No object indicates the object is being returned
            # in its minimal state: id + resource_uri
            # No issues sending down those bits of information
            return True

        course = object.asset.course

        # 1. User requesting information must be a member of the course
        #    OR a designated staff member
        if not course.is_member(request.user):
            return False

        # 2. Global annotations are accessible only to the author.
        if (object.is_global_annotation() and
                not request.user == object.author):
            return False

        # 3. User must be faculty OR
        # all course selections must be visible to all users
        if (course.is_faculty(request.user) or
                course_details.all_selections_are_visible(course)):
            return True

        # 4. Else, the user or a faculty member must be the selection author
        authorized = list(course.faculty)
        authorized.append(request.user)
        return object.author in authorized

    def apply_limits(self, request, object_list):
        # Limit the returned selection list to authorized items
        visible = []
        for o in object_list:
            if self.is_authorized(request, o):
                visible.append(o)

        return visible


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
