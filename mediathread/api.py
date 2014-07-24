#pylint: disable-msg=R0904
from courseaffils.lib import get_public_name
from courseaffils.models import Course, CourseInfo
from django.contrib.auth.models import User, Group
from tagging.models import Tag
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.constants import ALL
from tastypie.resources import ModelResource


'''From the TastyPie Docs:
Authentication is the component needed to verify who a certain user
is and to validate their access to the API.
Authentication answers the question "Who is this person?"
This usually involves requiring credentials, such as an API key or
username/password or oAuth tokens.'''


class ClassLevelAuthentication(Authentication):
    # All users must be logged into a specific class
    # before accessing the json API
    def is_authenticated(self, request, **kwargs):
        return (request.user.is_authenticated() and
                request.course and
                request.course.is_member(request.user))


'''From the TastyPie Docs:
Authorization is the component needed to verify what someone
can do with the resources within an API.

Authorization answers the question "Is permission granted for this user
to take this action?" This usually involves checking permissions such as
Create/Read/Update/Delete access, or putting limits on
what data the user can access.'''


class FacultyAuthorization(Authorization):
    def is_authorized(self, request, obj=None):
        return request.course.is_faculty(request.user)


class UserAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        request = bundle.request

        if request.user.is_staff:
            return object_list

        # As a precaution, verify the list is filtered by the current course
        course_members = [m.id for m in request.course.members]
        return object_list.filter(id__in=course_members)


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.none()
        excludes = ['first_name', 'last_name', 'email',
                    'password', 'is_active', 'is_staff', 'is_superuser',
                    'date_joined', 'last_login']
        allowed_methods = ['get']
        authentication = ClassLevelAuthentication()
        authorization = UserAuthorization()
        ordering = 'id'
        filtering = {'id': ALL,
                     'username': ALL}

    def dehydrate(self, bundle):
        bundle.data['public_name'] = get_public_name(bundle.obj,
                                                     bundle.request)
        return bundle

    def render_one(self, request, user):
        bundle = self.build_bundle(obj=user, request=request)
        dehydrated = self.full_dehydrate(bundle)
        return dehydrated.data

    def render_list(self, request, lst):
        data = []
        for user in lst:
            bundle = self.build_bundle(obj=user, request=request)
            dehydrated = self.full_dehydrate(bundle)
            data.append(dehydrated.data)
        return data


class GroupResource(ModelResource):
    user_set = fields.ToManyField('mediathread.api.UserResource',
                                  'user_set',
                                  full=True)

    class Meta:
        queryset = Group.objects.none()
        authentication = ClassLevelAuthentication()


class TagResource(ModelResource):
    class Meta:
        queryset = Tag.objects.none()
        list_allowed_methods = []
        detail_allowed_methods = []
        authentication = ClassLevelAuthentication()
        limit = 1000
        max_limit = 1000

    def dehydrate(self, bundle):
        if hasattr(bundle.obj, "count"):
            bundle.data['count'] = int(bundle.obj.count)
        bundle.data['last'] = hasattr(bundle.obj, "last")
        return bundle

    def render_list(self, request, tags):
        tag_last = len(tags) - 1
        data = []
        for idx, tag in enumerate(tags):
            if idx == tag_last:
                setattr(tag, 'last', idx == tag_last)

            bundle = self.build_bundle(obj=tag, request=request)
            dehydrated = self.full_dehydrate(bundle)
            data.append(dehydrated.data)
        return data

    def render_related(self, request, object_list):
        tags = Tag.objects.usage_for_queryset(object_list, counts=True)
        tags.sort(lambda a, b: cmp(a.name.lower(), b.name.lower()))

        tag_last = len(tags) - 1
        data = []
        for idx, tag in enumerate(tags):
            if idx == tag_last:
                setattr(tag, 'last', idx == tag_last)

            bundle = self.build_bundle(obj=tag, request=request)
            dehydrated = self.full_dehydrate(bundle)
            data.append(dehydrated.data)
        return data


class CourseMemberAuthorization(Authorization):

    def read_detail(self, object_list, bundle):
        lst = self.read_list(object_list, bundle)
        return len(lst) > 0

    def read_list(self, object_list, bundle):
        # User must be a member of all courses in the request list
        for course in object_list:
            if not course.is_member(bundle.request.user):
                return Course.objects.none()

        return object_list


class CourseInfoResource(ModelResource):
    class Meta:
        queryset = CourseInfo.objects.none()
        resource_name = 'info'
        allowed_methods = ['get']
        excludes = ['days', 'endtime', 'starttime']

    def render_one(self, request, course):
        bundle = self.build_bundle(obj=course, request=request)
        dehydrated = self.full_dehydrate(bundle)
        return self._meta.serializer.to_simple(dehydrated, None)


class CourseResource(ModelResource):
    faculty_group = fields.ForeignKey(GroupResource,
                                      'faculty_group',
                                      full=True)
    group = fields.ForeignKey(GroupResource,
                              'group',
                              full=True)

    info = fields.ForeignKey(CourseInfoResource, 'info',
                             full=True, blank=True, null=True)

    class Meta:
        queryset = Course.objects.all()
        resource_name = "course_summary"
        list_allowed_methods = []
        detail_allowed_methods = ['get']

        # User is logged into some course
        authentication = ClassLevelAuthentication()

        # User is a member of this course
        authorization = CourseMemberAuthorization()

    def render_one(self, request, course):
        bundle = self.build_bundle(obj=course, request=request)
        dehydrated = self.full_dehydrate(bundle)
        return self._meta.serializer.to_simple(dehydrated, None)
