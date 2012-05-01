from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns(
    'projects.views',
    
    url(r'^create/$', 'project_create', name="project-create"),
    
    url(r'^view/(?P<project_id>\d+)/$', 'project_workspace', name="project-workspace"),
    
    url(r'^save/(?P<project_id>\d+)/$', 'project_save', name='project-save'),
    
    url(r'^delete/(?P<project_id>\d+)/$', 'project_delete', name='project-delete'),
    
    # view versioned read only 
    url(r'^view/(?P<project_id>\d+)/version/(?P<version_number>\d+)/$',
        'project_view_readonly', name='project-view-readonly'),
                       
    # view public url - read only view.
    # Note: StructuredCollaboration requires 
    # 1. Url structure must be <classname>/<instance_id>/
    # 2. Name must be <class>-view to do a reverse           
    url(r'^(?P<project_id>\d+)/', 'project_view_readonly', name="project-view")    
)
