from django.conf.urls.defaults import patterns, url
from mediathread.assetmgr.views import AssetWorkspaceView, AssetReferenceView
import os.path

media_root = os.path.join(os.path.dirname(__file__), "media")

urlpatterns = patterns(
    'mediathread.assetmgr.views',

    # Archive save or delete
    url(r'^archive/$',
        'archive_add_or_remove',
        name="archive-add-or-remove"),

    # Archive save or delete
    url(r'^references/(?P<asset_id>\d+)/$', AssetReferenceView.as_view(),
        {}, "asset-references"),

    # Goto the most recently created asset by user
    url(r'^most_recent/$', 'most_recent', name='asset-most-recent'),

    url(r'^(?P<asset_id>\d+)/$', AssetWorkspaceView.as_view(),
        {}, 'asset-view'),

    url(r'^(?P<asset_id>\d+)/annotations/(?P<annot_id>\d+)/$',
        AssetWorkspaceView.as_view(), {}, 'annotation-view'),

    url(r'^create/(?P<asset_id>\d+)/annotations/$', 'annotation_create'),

    url(r'^create/(?P<asset_id>\d+)/global/$', 'annotation_create_global'),

    url(r'^save/(?P<asset_id>\d+)/annotations/(?P<annot_id>\d+)/$',
        'annotation_save',
        name="annotation-save"),

    url(r'^delete/(?P<asset_id>\d+)/annotations/(?P<annot_id>\d+)/$',
        'annotation_delete',
        name="annotation-delete"),

    url(r'^delete/(?P<asset_id>\d+)/$', 'asset_delete', name='asset-delete'),

    url(r'^xmeml/(?P<asset_id>\w+)/$',
        'final_cut_pro_xml',
        name="final_cut_pro_xml"),

    # Asset workspace variations
    url(r'^$', AssetWorkspaceView.as_view(), {}, 'asset-collection-view'),
)
