from django.db import models
from django.db.models import get_model,Max
from django.contrib import comments
from django.contrib.comments.models import COMMENT_MAX_LENGTH
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from django.core import urlresolvers
from django.conf import settings

ThreadedComment = get_model('threadedcomments', 'threadedcomment')
Collaboration = get_model('structuredcollaboration', 'collaboration')
ContentType = get_model('contenttypes','contenttype')


def get_discussions( arbitrary_object):
    coll = ContentType.objects.get_for_model(Collaboration)
    discussions = []
    for d in ThreadedComment.objects.filter(parent=None, content_type = coll):
        if d.content_object and d.content_object._parent_id and \
                arbitrary_object == d.content_object._parent.content_object:
            discussions.append(d)
    return discussions  

def threaded_comment_json(comment):
    data = { 
        'type': 'discussion',
        'form': comments.get_form()(comment.content_object).__unicode__(),
        'editing': True,
        'discussion': {
            'id': comment.id,
            'max_length': COMMENT_MAX_LENGTH
         }
    }
    return data
                      
                    
          


