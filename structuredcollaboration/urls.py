from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'structuredcollaboration.views',

    url(r'^collaboration/(?P<collab_id>\d+)/$',
        'collaboration_dispatch',
        name='collaboration-dispatch'),

    url(r'^(?P<context_slug>\w+)/(?P<collab_id>\d+)/',
        'view_collab_by_collab',
        name='collaboration-view'),
    # alternate way:
    url(r'^(?P<context_slug>\w+)/(?P<obj_type>\w+)/(?P<obj_id>\d+)/',
        'view_collab_by_obj',
        name='collaboration-obj-view'),
    url(r'^(?P<context_slug>\w+)/(?P<collab_slug>\w+)/',
        'view_collab_by_slug',
        name='collaboration-slug-view'),
)
