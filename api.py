from courseaffils.lib import get_public_name
from django.contrib.auth.models import User, Group
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource


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
        return object_list.filter(id_in=[id for m in request.course.members()])


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.none()
        excludes = ['first_name', 'last_name', 'username', 'email',
                    'password', 'is_active', 'is_staff', 'is_superuser',
                    'date_joined', 'last_login']
        allowed_methods = ['get']
        authentication = ClassLevelAuthentication()
        authorization = UserAuthorization()

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
