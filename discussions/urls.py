from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'discussions.views',

    url(r'^create/$', 'discussion_create', name='discussion-create'),

    url(r'^delete/(?P<discussion_id>\d+)/$',
        'discussion_delete',
        name='discussion-delete'),

    url(r'^(?P<discussion_id>\d+)/$',
        'discussion_view',
        name='discussion-view'),

    url(r'^show/(?P<discussion_id>\d+)/$',
        'discussion_view',
        name='discussion-show'),

    url(r'^comment/(?P<comment_id>\d+)$',
        'comment_save',
        name='comment-save'),
)
