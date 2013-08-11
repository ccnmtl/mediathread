from django.conf.urls.defaults import patterns, url
import os.path

media_root = os.path.join(os.path.dirname(__file__), "media")

urlpatterns = patterns(
    'mediathread.taxonomy.views',

    url(r'^create/$',
        'vocabulary_create'),
    url(r'^delete/(?P<vocabulary_id>\d+)/$',
        'vocabulary_delete',
        name='vocabulary-delete'),
    url(r'^save/(?P<vocabulary_id>\d+)/$',
        'vocabulary_save'),

    url(r'term/create/(?P<vocabulary_id>\d+)/$',
        'term_create'),
    url(r'term/delete/(?P<term_id>\d+)/$',
        'term_delete'),

    url(r'^$',
        'taxonomy_workspace',
        name='taxonomy-workspace'),

    url(r'^/(?P<vocabulary_id>\d+)/$',
        'taxonomy_workspace',
        name='taxonomy-workspace-view')
)
