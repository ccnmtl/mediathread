#pylint: disable-msg=R0904
from courseaffils.lib import get_public_name
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from mediathread.djangosherd.models import SherdNote
from mediathread.main.course_details import all_selections_are_visible, \
    cached_course_is_faculty
from tagging.models import Tag
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.bundle import Bundle
from tastypie.constants import ALL
from tastypie.exceptions import ApiFieldError, BadRequest, InvalidSortError
from tastypie.fields import ToManyField
from tastypie.resources import ModelResource
import re


class ToManyFieldEx(ToManyField):
    def build_m2m_filters(self, resource, filters, related_field_name):
        related_filters = {}
        pattern = '^.*%s__' % related_field_name

        for key, value in filters.items():
            if re.match(pattern, key):
                key = re.sub(pattern, '', key)
                related_filters[key] = value

        return resource.build_filters(related_filters)

    def apply_m2m_filters(self, request, related_field_name, object_list):
        m2m_resource = self.get_related_resource(None)

        applicable_filters = self.build_m2m_filters(m2m_resource,
                                                    request.GET.copy(),
                                                    related_field_name)

        try:
            if applicable_filters:
                object_list = object_list.filter(
                    **applicable_filters).distinct()

            return m2m_resource.apply_authorization_limits(request,
                                                           object_list)
        except ValueError:
            raise BadRequest("Invalid resource lookup data \
            provided (mismatched type).")

    def apply_sorting(self, request, object_list):
        m2m_resource = self.get_related_resource(None)
        return m2m_resource.apply_sorting(object_list, options=request.GET)

    def dehydrate(self, bundle):
        if not bundle.obj or not bundle.obj.pk:
            if not self.null:
                raise ApiFieldError("The model '%r' does not have a primary \
                    key and can not be used in a ToMany context." % bundle.obj)

            return []

        the_m2ms = None
        previous_obj = bundle.obj
        attr = self.attribute

        if isinstance(self.attribute, basestring):
            attrs = self.attribute.split('__')
            the_m2ms = bundle.obj

            for attr in attrs:
                previous_obj = the_m2ms
                try:
                    the_m2ms = getattr(the_m2ms, attr, None)
                    the_m2ms = self.apply_m2m_filters(bundle.request,
                                                      attr,
                                                      the_m2ms.all())
                except ObjectDoesNotExist:
                    the_m2ms = None

                if not the_m2ms:
                    break

                try:
                    the_m2ms = self.apply_sorting(bundle.request,
                                                  the_m2ms.all())
                except InvalidSortError:
                    pass

        elif callable(self.attribute):
            the_m2ms = self.attribute(bundle)

        if not the_m2ms:
            if not self.null:
                raise ApiFieldError("The model '%r' has an empty attribute \
                                    '%s' and doesn't allow a null value."
                                    % (previous_obj, attr))

            return []

        self.m2m_resources = []
        m2m_dehydrated = []

        # TODO: Also model-specific and leaky. Relies on there being a
        #       ``Manager`` there.
        for m2m in the_m2ms.select_related():
            m2m_resource = self.get_related_resource(m2m)
            m2m_bundle = Bundle(obj=m2m, request=bundle.request)
            self.m2m_resources.append(m2m_resource)
            m2m_dehydrated.append(self.dehydrate_related(m2m_bundle,
                                                         m2m_resource))

        return m2m_dehydrated


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
    def apply_limits(self, request, object_list):
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


class RestrictedCourseResource(ModelResource):
    def __init__(self, course=None):
        super(RestrictedCourseResource, self).__init__(None)
        self.course = course

    def get_unrestricted(self, request, object_list, course):
        return object_list

    def get_restricted(self, request, object_list, course):
        return []

    def apply_authorization_limits(self, request, object_list):
        course = self.course or request.course

        if (all_selections_are_visible(course) or
                cached_course_is_faculty(course, request.user)):
            return self.get_unrestricted(request, object_list, course)
        else:
            return self.get_restricted(request, object_list, course)


class TagResource(RestrictedCourseResource):
    def __init__(self, course=None):
        super(TagResource, self).__init__(None)
        self.filters = {}

    class Meta:
        queryset = Tag.objects.none()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        authentication = ClassLevelAuthentication()
        limit = 1000
        max_limit = 1000

    def dehydrate(self, bundle):
        if hasattr(bundle.obj, "count"):
            bundle.data['count'] = int(bundle.obj.count)
        bundle.data['last'] = hasattr(bundle.obj, "last")
        return bundle

    def _filter_tags(self, note_set):
        if 'assets' in self.filters:
            note_set = note_set.filter(asset__id__in=self.filters['assets'])
        if 'record_owner' in self.filters:
            note_set = note_set.filter(author=self.filters['record_owner'])

        counts = 'counts' in self.filters
        tags = Tag.objects.usage_for_queryset(note_set, counts=counts)
        tags.sort(lambda a, b: cmp(a.name.lower(), b.name.lower()))
        return tags

    def get_unrestricted(self, request, object_list, course):
        notes = SherdNote.objects.filter(asset__course=course)
        return self._filter_tags(notes)

    def get_restricted(self, request, object_list, course):
        whitelist = [f.id for f in course.faculty]
        whitelist.append(request.user.id)

        notes = SherdNote.objects.filter(asset__course=course,
                                         author__id__in=whitelist)
        return self._filter_tags(notes)

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

    def filter(self, request, filters):
        self.filters = filters
        objects = self.obj_get_list(request=request)
        return self.render_list(request, objects)
