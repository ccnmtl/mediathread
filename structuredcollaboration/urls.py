from django.conf.urls import patterns, url

urlpatterns = patterns(
    'structuredcollaboration.views',

    url(r'^(?P<context_slug>\w+)/(?P<obj_type>\w+)/(?P<obj_id>\d+)/',
        'view_collab_by_obj',
        name='collaboration-obj-view'),
)
