from django.conf.urls.defaults import *
from django.conf import settings

import projects

urlpatterns = patterns(
    'mediathread_main.views',

    url(r'^$',
        'class_listing',
        name='class-listing'),
    
    url(r'^portal$',
        'class_portal',
        name='class-portal'),
    
    #narrowly overrides the username space below for a project_id just numbers
    (r'', include('projects.urls')),

    url(r'^(?P<user_name>\w[^/]*)/$',
        'your_space',
        name='your-space'),


    url(r'^(?P<user_name>\w[^/]*)/asset/(?P<asset_id>\d+)/$',
        'remove_record',
        name='my-asset-notes'
        ),


    url(r'^(?P<user_name>\w[^/]*)/asset/$',
        'your_records',
        name='your-space-records'),



    )

