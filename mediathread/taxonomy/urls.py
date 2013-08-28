from django.conf.urls.defaults import patterns, url
import os.path

media_root = os.path.join(os.path.dirname(__file__), "media")

urlpatterns = patterns(
    'mediathread.taxonomy.views',

    url(r'^$',
        'taxonomy_workspace',
        name='taxonomy-workspace'),

    url(r'^/(?P<vocabulary_id>\d+)/$',
        'taxonomy_workspace',
        name='taxonomy-workspace-view')
)
