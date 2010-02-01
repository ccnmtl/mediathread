from django.conf.urls.defaults import *
from django.conf import settings
urlpatterns = patterns(

    #show a discussion:    
    'discussions.views', url(r'^show/(?P<discussion_id>\d+)$', 'show', name='show_discussion'),

    #create a new discussion of an arbitrary model instance:
    (r'^new/$', 'new'),

    #TODO: override comments posted view:    
    #(r'^comments/posted/$', 'my_comment_posted'),
    )
