from django.conf.urls.defaults import *
from django.conf import settings
import os.path

media_root = os.path.join(os.path.dirname(__file__),"media")

urlpatterns = patterns(
    'djangosherd.views',
    #all in /annotations/ (from ./urls.py)
    url(r'^all/$', 
        'annotations_collection_fragment', name="all-annotations-fragment"),

    url(r'^tags.json$', 
        'tags_json', name="all-annotation-tags"),

    url(r'^(?P<username>none)/$', 
        'annotations_collection_fragment', name="annotations-fragment-none"),

    url(r'^(?P<username>\w[^/]*)/$', 
        'annotations_collection_fragment', name="annotations-fragment"),

    url(r'^iframe/(?P<asset_id>\w+)/(?P<annot_id>\w+)/$', 
        'annotation_iframe_view', name="annotation-iframe"),

    url(r'^json/(?P<annot_id>\w+)/$', 
        'annotation_json', name="annotation-json"),

    url(r'^xmeml/(?P<annot_id>\w+)/$', 
        'final_cut_pro_xml', name="final_cut_pro_xml"),

    )
