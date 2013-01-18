from courseaffils.lib import get_public_name
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.bundle import Bundle
from tastypie.constants import ALL
from tastypie.fields import ToManyField
from tastypie.resources import ModelResource
from tastypie.exceptions import ApiFieldError, BadRequest
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

    def apply_m2m_filters(self, request, related_field_name, base_object_list):
        m2m_resource = self.get_related_resource(None)

        applicable_filters = self.build_m2m_filters(m2m_resource,
                                                    request.GET.copy(),
                                                    related_field_name)

        try:
            if applicable_filters:
                base_object_list = base_object_list.filter(
                    **applicable_filters).distinct()

            return m2m_resource.apply_authorization_limits(request,
                                                           base_object_list)
        except ValueError:
            raise BadRequest("Invalid resource lookup data \
            provided (mismatched type).")

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
        for m2m in the_m2ms.all():
            m2m_resource = self.get_related_resource(m2m)
            m2m_bundle = Bundle(obj=m2m, request=bundle.request)
            self.m2m_resources.append(m2m_resource)
            m2m_dehydrated.append(self.dehydrate_related(m2m_bundle,
                                                         m2m_resource))

        return m2m_dehydrated


class ClassLevelAuthentication(Authentication):
    # All users must be logged into a specific class
    # before accessing the json API
    def is_authenticated(self, request, **kwargs):
        return (request.user.is_authenticated() and
                request.course and
                request.course.is_member(request.user))


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
        excludes = ['first_name', 'last_name', 'username', 'email',
                    'password', 'is_active', 'is_staff', 'is_superuser',
                    'date_joined', 'last_login']
        allowed_methods = ['get']
        authentication = ClassLevelAuthentication()
        authorization = UserAuthorization()
        ordering = 'id'
        filtering = {'id': ALL}

    def dehydrate(self, bundle):
        bundle.data['full_name'] = get_public_name(bundle.obj, bundle.request)
        return bundle


class GroupResource(ModelResource):
    user_set = fields.ToManyField('mediathread.api.UserResource',
                                  'user_set',
                                  full=True)

    class Meta:
        queryset = Group.objects.none()
        allowed_methods = ['get']
        authentication = ClassLevelAuthentication()
