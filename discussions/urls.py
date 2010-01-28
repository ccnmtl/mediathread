from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns(

    #'structuredcollaboration.views',
    #
    #url(r'^(?P<context_slug>\w+)/(?P<obj_type>\w+)/(?P<obj_id>\d+)/$',
    #    'view_collaboration',
    #    name='collaboration-view'),

    'discussions.views', url(r'^show/(?P<obj_id>\d+)$', 'show', name='show_discussion'),
    )

