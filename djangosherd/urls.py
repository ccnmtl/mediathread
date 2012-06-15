from django.conf.urls.defaults import *
from django.conf import settings
import os.path

media_root = os.path.join(os.path.dirname(__file__),"media")

urlpatterns = patterns(
    'djangosherd.views',
    
    #all in /annotations/ (from ./urls.py)
    url(r'^tags.json$', 
        'tags_json', name="all-annotation-tags"),

    url(r'^json/(?P<annot_id>\w+)/$', 
        'annotation_json', name="annotation-json"),

    )
