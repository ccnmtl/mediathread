from django.conf.urls import url

from mediathread.discussions.views import (
    DiscussionView, DiscussionDeleteView, discussion_create,
    comment_save
)


urlpatterns = [
    url(r'^create/$', discussion_create, name='discussion-create'),

    url(r'^delete/(?P<discussion_id>\d+)/$',
        DiscussionDeleteView.as_view(), {},
        name='discussion-delete'),

    url(r'^comment/(?P<comment_id>\d+)/$',
        comment_save,
        name='comment-save'),

    url(r'^(?P<discussion_id>\d+)/$',
        DiscussionView.as_view(), {}, 'discussion-view'),

]
