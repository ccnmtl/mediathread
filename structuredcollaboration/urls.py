from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns(
    'structuredcollaboration.views',

    url(r'^(?P<context_slug>\w+)/(?P<collab_id>\d+)/',
        'view_collab_by_collab',
        name='collaboration-view'),
    url(r'^(?P<context_slug>\w+)/(?P<collab_slug>\w+)/',
        'view_collab_by_slug',
        name='collaboration-slug-view'),
    #alternate way:
    url(r'^(?P<context_slug>\w+)/(?P<obj_type>\w+)/(?P<obj_id>\d+)/',
        'view_collab_by_obj',
        name='collaboration-obj-view'),


    )

