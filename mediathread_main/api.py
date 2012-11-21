from django.contrib.auth.models import User, Group
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from courseaffils.models import *
from courseaffils.lib import get_public_name
from projects.models import Project
from assetmgr.models import Asset
from djangosherd.models import SherdNote

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.none()
        excludes = ['first_name', 'last_name', 'username', 'email', 'password', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login']
        allowed_methods = ['get']
        
    def dehydrate(self, bundle):
        bundle.data['full_name'] = get_public_name(bundle.obj, bundle.request)
        return bundle

class GroupResource(ModelResource):
    user_set = fields.ToManyField('mediathread_main.api.UserResource', 'user_set', full=True)
    
    class Meta:
        queryset = Group.objects.none()
        allowed_methods = ['get']


class SherdNoteResource(ModelResource):
    class Meta:
        queryset = SherdNote.objects.none()
        excludes = ['tags', 'body', 'added', 'modified', 'range1', 'range2', 'annotation_data']
        allowed_methods = "get"      
        
    def dehydrate(self, bundle):
        bundle.data['is_global_annotation'] = bundle.obj.is_null()      
        return bundle   
      
class ProjectResource(ModelResource):
    citations = fields.ToManyField('mediathread_main.api.SherdNoteResource',
        blank=True, null=True, full=True,
        attribute=lambda bundle: SherdNote.objects.filter(pk__in=[c.id for c in bundle.obj.citations()]))

    class Meta:
        queryset = Project.objects.none()
        excludes = ['author', 'participants', 'body', 'submitted', 'feedback']
        allowed_methods = ['get']
    
        
    def dehydrate(self, bundle):
        bundle.data['is_assignment'] = bundle.obj.visibility_short() == 'Assignment' 
        bundle.data['attribution'] = bundle.obj.attribution()
        return bundle
    
class AssetResource(ModelResource):
    author = fields.ForeignKey(UserResource, 'author', full=True)
    sherdnote_set = fields.ToManyField('mediathread_main.api.SherdNoteResource',
        "sherdnote_set",
        blank=True, null=True, full=True)
    
    class Meta:
        queryset = Asset.objects.none()
        excludes = ['added', 'modified', 'course', 'active', 'metadata_blob']
        allowed_methods = ['get']        
        
    def dehydrate(self, bundle):
        bundle.data['thumb_url'] = bundle.obj.thumb_url
        bundle.data['primary_type'] = bundle.obj.primary.label
        return bundle
        
class CourseInfoResource(ModelResource):
    class Meta:
        queryset = CourseInfo.objects.none()
        resource_name = 'info'         
        allowed_methods = ['get']
        excludes = ['days', 'endtime', 'starttime']
        
class CourseAuthorization(Authorization):
    def is_authorized(self, request, object=None):
        return request.course.is_faculty(request.user)
    
class CourseResource(ModelResource):
    faculty_group = fields.ForeignKey(GroupResource, 'faculty_group', full=True)
    info = fields.ForeignKey(CourseInfoResource, 'info', full=True, blank=True, null=True)
    project_set = fields.ToManyField('mediathread_main.api.ProjectResource',
        blank=True, null=True, full=True,
        attribute=lambda bundle: Project.objects.filter(bundle.obj.faculty_filter))
    item_set = fields.ToManyField('mediathread_main.api.AssetResource',
        blank=True, null=True, full=True,
        attribute=lambda bundle: Asset.objects.filter(bundle.obj.faculty_filter))

    class Meta:
        queryset = Course.objects.all()
        excludes = ['group']
        allowed_methods = ['get']
        authorization = CourseAuthorization()
    
    def dehydrate(self, bundle):
        # Unable to completely filter the project_set using QuerySet
        # due to complexity of the StructuredCollaboration architecture
        # Iterate all projects to remove private + assignment responses
        lst = []
        for project in bundle.data['project_set']:
            if project.obj.class_visible() and not project.obj.assignment():
                lst.append(project)
        bundle.data['project_set'] = lst
        
        # Remove any citations 
        return bundle
            
    
        