from django.contrib.auth.models import User, Group
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from courseaffils.models import *
from mediathread.api import *
from projects.models import Project
from djangosherd.models import SherdNote

class ProjectAuthorization(Authorization):
    def apply_limits(self, request, object_list):
        # remove any projects that are not visible to the requested user
        visible = []
        for l in lst:
            if l.visible(request):
                visible.append(l)
                                
        return visible
        
class ProjectResource(ModelResource):
    selections = fields.ToManyField('djangosherd.api.SherdNoteResource',
        blank=True, null=True, full=True,
        attribute=lambda bundle: \
            SherdNote.objects.filter(pk__in=[c.id for c in bundle.obj.citations()]))
            # By default, all citations within a visible project are also visible

    class Meta:
        queryset = Project.objects.none()
        excludes = ['author', 'participants', 'body', 'submitted', 'feedback']
        allowed_methods = ['get']
        authentication = ClassLevelAuthentication()
        
    def dehydrate(self, bundle):
        bundle.data['is_assignment'] = bundle.obj.visibility_short() == 'Assignment'
        bundle.data['is_response'] = bundle.obj.assignment() != None
        bundle.data['attribution'] = bundle.obj.attribution()
        return bundle