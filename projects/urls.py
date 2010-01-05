from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns(
    'projects.views',

    #narrowly overrides the username space
    #when it's just numbers
    url(r'^(?P<project_id>\d+)/$',
        'project_readonly_view',
        name='project-view'),

    url(r'^(?P<user_name>\w+)/project/$',
        'your_projects',
        name='your-space-projects',
        ),
        
    url(r'^(?P<user_name>\w+)/project/(?P<project_id>\d+)/$',
        'view_project',
        name='project-workspace',
        ),

    url(r'^(?P<user_name>\w+)/project/(?P<project_id>\d+)/version/(?P<version_id>\d+)/$',
        'project_version_preview',
        name='project_version_preview',
        ),


    )

