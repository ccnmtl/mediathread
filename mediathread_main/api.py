from django.contrib.auth.models import User, Group
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from courseaffils.models import *

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser', 'date_joined']
        allowed_methods = ['get']

class GroupResource(ModelResource):
    user_set = fields.ToManyField('mediathread_main.api.UserResource', 'user_set', full=True)
    
    class Meta:
        queryset = Group.objects.all()
        resource_name = 'group'
        allowed_methods = ['get']
        
class CourseInfoResource(ModelResource):
    class Meta:
        queryset = CourseInfo.objects.all()
        resource_name = 'info'         
        allowed_methods = ['get']
        excludes = ['days', 'endtime', 'starttime']
        
class CourseAuthorization(Authorization):
    def is_authorized(self, request, object=None):
        return request.course.is_faculty(request.user)

class CourseResource(ModelResource):
    faculty_group = fields.ForeignKey(GroupResource, 'faculty_group', full=True)
    info = fields.ForeignKey(CourseInfoResource, 'info', full=True)

    class Meta:
        queryset = Course.objects.all()
        resource_name = 'course'
        excludes = ['group']
        allowed_methods = ['get']
        authorization = CourseAuthorization()

        