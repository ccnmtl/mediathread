from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns(
    'discussions.views', 

    url(r'^new/$', 'discussion_create', name='discussion-create'),
    
    url(r'^delete/(?P<discussion_id>\d+)/$', 'discussion_delete', name='discussion-delete'),

    url(r'^(?P<discussion_id>\d+)/$', 'discussion_view', name='discussion-view'),
    url(r'^show/(?P<discussion_id>\d+)/$', 'discussion_view', name='discussion-show'),
    
    url(r'^comment/(?P<comment_id>\d+)$', 'comment_save', name='comment-save'),
)
