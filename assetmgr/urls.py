from django.conf.urls.defaults import *
from django.conf import settings
import os.path

media_root = os.path.join(os.path.dirname(__file__),"media")

urlpatterns = patterns(
    'assetmgr.views',

    url(r'^json/(?P<asset_id>\d+)/$', 
        'asset_json', name="asset-json"),

    url(r'^(?P<asset_id>\d+)/$', 
        'asset_workspace', name="asset-view"),

    url(r'^(?P<asset_id>\d+)/annotations/$',
        'create_annotations_container',
        name="create-annotations-container"),
                       
    url(r'^(?P<asset_id>\d+)/annotations/(?P<annot_id>\d+)/$',
        'annotationview',
        name="annotation-form"),
    )
