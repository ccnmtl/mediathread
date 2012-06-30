from django.conf.urls.defaults import *
from django.conf import settings
import os.path

media_root = os.path.join(os.path.dirname(__file__),"media")

urlpatterns = patterns(
    'assetmgr.views',

    url(r'^$', 'new_asset_workspace', name="new-asset-workspace"),
    
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
    
    url(r'^xmeml/(?P<asset_id>\w+)/$', 'final_cut_pro_xml', name="final_cut_pro_xml"),
)

