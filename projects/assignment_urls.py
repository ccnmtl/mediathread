from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns(
    'projects.views',

    #narrowly overrides the username space
    #when it's just numbers
    #[^v/]* is so we can do a json query with a different url
    #to avoid Chrome bug of replacing cache with 
    url(r'^editor/',
        'assignment_editor',
        name='assignment-editor',
        ),


    )