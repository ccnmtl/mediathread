from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns(
    'projects.views',

    #narrowly overrides the username space
    #when it's just numbers
    #[^v/]* is so we can do a json query with a different url
    #to avoid Chrome bug of replacing cache with 
    url(r'^(?P<project_id>\d+)/[^v/]*$',
        'project_readonly_view',
        name='project-view'),

    url(r'^(?P<user_name>\w+)/project/$',
        'your_projects',
        name='your-space-projects',
        ),

    url(r'^project/(?P<project_id>\d+)/version/(?P<version_number>\d+)/[^v/]*$',
        'project_version_preview',
        name='project_version_preview',
        ),
    url(r'^project/(?P<project_id>\d+)/[^v/]*$',
        'view_project',
        name='project-workspace',
        ),
    url(r'^projectversion/(?P<projectversion_id>\d+)/[^v/]*$',
        'project_version_view',
        name='projectversion-view',
        ),


    )

