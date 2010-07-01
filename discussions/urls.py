from django.conf.urls.defaults import *
from django.conf import settings
urlpatterns = patterns(
    'discussions.views', 

    #create a new discussion of an arbitrary model instance:
    (r'^new/$', 'new'),

    url(r'^show/(?P<discussion_id>\d+)$', 'show', 
        name='show_discussion'),

    url(r'^(?P<discussion_id>\d+)$', 'show', 
        name='discussion-view'),

    ##SYNC with absolute url in media/js/discussion.js
    url(r'^comment/(?P<comment_id>\d+)$', 'comment_change', 
        name='update-discussion-comment'),
    )
