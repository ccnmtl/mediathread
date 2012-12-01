from django.contrib.auth.models import User, Group
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from courseaffils.models import *
from courseaffils.lib import get_public_name
from mediathread.api import *
from projects.models import Project
from projects.api import ProjectAuthorization
from assetmgr.models import Asset
#from assetmgr.api import AssetAuthorization
from djangosherd.api import SherdNoteAuthorization
from djangosherd.models import SherdNote
    
class AssetResource(ModelResource):
    author = fields.ForeignKey(UserResource, 'author', full=True)
    selections = fields.ToManyField('djangosherd.api.SherdNoteResource',
        blank=True, null=True, full=True, 
        attribute=lambda bundle: SherdNoteAuthorization().\
            apply_limits(bundle.request, bundle.obj.sherdnote_set.all()))
    
    class Meta:
        queryset = Asset.objects.none()
        excludes = ['added', 'modified', 'course', 'active', 'metadata_blob']
        allowed_methods = ['get']
        authentication = ClassLevelAuthentication()
        
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
        return object and object.is_member(request.user)    
    
class CourseResource(ModelResource):
    faculty_group = fields.ForeignKey(GroupResource, 'faculty_group', full=True)
    info = fields.ForeignKey(CourseInfoResource, 'info', full=True, blank=True, null=True)
    
    project_set = fields.ToManyField('mediathread_main.api.ProjectResource',
        blank=True, null=True, full=True,
        attribute=lambda bundle: ProjectAuthorization(). \
            apply_limits(bundle.request, bundle.obj.project_set.all()))
    
    item_set = fields.ToManyField('mediathread_main.api.AssetResource',
        blank=True, null=True, full=True,
        attribute=lambda bundle: Asset.objects.references(bundle.obj, bundle.obj.faculty))

    class Meta:
        queryset = Course.objects.all()
        excludes = ['group']
        allowed_methods = ['get']
        
        # User is logged into some course
        authentication = ClassLevelAuthentication()
        
        # User has access to the requested object
        authorization = CourseAuthorization()
            
    
        