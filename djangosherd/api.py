from tastypie import fields
from tastypie.resources import ModelResource
from mediathread.api import ClassLevelAuthentication
from tastypie.authorization import Authorization
from djangosherd.models import SherdNote
from mediathread_main import course_details
from mediathread.api import *

class SherdNoteAuthorization(Authorization):
    def is_authorized(self, request, object=None):
        if not object:
            return True
        
        course = object.asset.course
        
        # User must be in this course
        if not course.is_member(request.user):
            return False
        
        # User must be faculty OR all course selections must be visible
        if course.is_faculty(request.user) or \
            course_details.all_selections_are_visible(course):            
            return True
        
        # Else, the user must be the author of the note
        set = course.faculty()
        set.append(request.user)        
        return object.author in set
    
    def apply_limits(self, request, object_list):
        visible = []
        for o in object_list:
            if self.is_authorized(request, o):
                visible.append(o)
        
        return visible

class SherdNoteResource(ModelResource):
    author = fields.ForeignKey(UserResource, 'author', full=True)
    
    class Meta:
        queryset = SherdNote.objects.all()
        excludes = ['tags', 'body', 'added', 'modified', 'range1', 'range2', 'annotation_data']
        allowed_methods = "get"
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        
        # User is logged into some course
        authentication = ClassLevelAuthentication()
        
        # User is authorized to look at this particular SherdNote
        authorization = SherdNoteAuthorization()
        
    def dehydrate(self, bundle):
        bundle.data['asset_id'] = str(bundle.obj.asset.id)
        bundle.data['is_global_annotation'] = str(bundle.obj.is_global_annotation())
        return bundle