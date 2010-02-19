from django.conf.urls.defaults import *
from django.conf import settings
import os.path

media_root = os.path.join(os.path.dirname(__file__),"media")

urlpatterns = patterns(
    'djangosherd.views',

    url(r'^(?P<username>\w+)/$', 
        'annotations_collection_fragment', name="annotations-fragment"),

    url(r'^iframe/(?P<asset_id>\w+)/(?P<annot_id>\w+)/$', 
        'annotation_iframe_view', name="annotation-iframe"),

    url(r'^json/(?P<annot_id>\w+)/$', 
        'annotation_json', name="annotation-json"),

    )
