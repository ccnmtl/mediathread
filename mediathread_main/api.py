import copy
from django.contrib.auth.models import User, Group
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from courseaffils.models import *
from projects.models import Project

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        excludes = ['first_name', 'last_name', 'username', 'email', 'password', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login']
        allowed_methods = ['get']
        
    def dehydrate(self, bundle):
        bundle.data['full_name'] = bundle.obj.get_full_name() or bundle.obj.username
        return bundle

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
      
class ProjectResource(ModelResource):
    class Meta:
        queryset = Project.objects.none()
        resource_name = 'project'
        excludes = ['author', 'participants', 'body', 'submitted', 'feedback']
        allowed_methods = ['get']

    def dehydrate(self, bundle):
        bundle.data['is_assignment'] = bundle.obj.is_assignment(bundle.request)
        return bundle
    
class CourseAuthorization(Authorization):
    def is_authorized(self, request, object=None):
        return request.course.is_faculty(request.user)
    
class CourseResource(ModelResource):
    faculty_group = fields.ForeignKey(GroupResource, 'faculty_group', full=True)
    info = fields.ForeignKey(CourseInfoResource, 'info', full=True, blank=True, null=True)
    project_set = fields.ToManyField('mediathread_main.api.ProjectResource',
        blank=True, null=True, full=True,
        attribute=lambda bundle: Project.objects.filter(bundle.obj.faculty_filter))

    class Meta:
        queryset = Course.objects.all()
        resource_name = 'course'
        excludes = ['group']
        allowed_methods = ['get']
        authorization = CourseAuthorization()
    
    def dehydrate(self, bundle):
        # Unable to completely filter the project_set using QuerySet
        # Iterate all projects to remove private + assignment responses
        lst = []
        for project in bundle.data['project_set']:
            if project.obj.class_visible() and not project.obj.assignment():
                lst.append(project)
        bundle.data['project_set'] = lst
        return bundle
            
    
        