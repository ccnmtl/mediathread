from django.conf.urls.defaults import patterns, url
import os.path

media_root = os.path.join(os.path.dirname(__file__), "media")

urlpatterns = patterns(
    'mediathread.assetmgr.views',

    # Archive save or delete
    url(r'^archive/$',
        'archive_add_or_remove',
        name="archive-add-or-remove"),

    # Archive save or delete
    url(r'^references/(?P<asset_id>\d+)/$',
        'asset_references',
        name="asset-references"),

    # Asset workspace variations
    url(r'^$',
        'asset_workspace',
        name='asset-collection-view'),

    # Goto the most recently created asset by user
    url(r'^most_recent/$',
        'most_recent',
        name='asset-most-recent'),

    url(r'^(?P<asset_id>\d+)/$',
        'asset_workspace',
        name="asset-view"),

    url(r'^(?P<asset_id>\d+)/annotations/(?P<annot_id>\d+)/$',
        'asset_workspace',
        name='annotation-view'),

    # json render all assets for a cource
    url(r'^json/course/$',
        'assets_by_course',
        name='assets-by-course'),

    # json render all assets for a specific user
    url(r'^json/user/(?P<record_owner_name>\w[^/]*)/$',
        'assets_by_user',
        name='assets-by-user'),

    # json render for a specific asset
    url(r'^json/(?P<asset_id>\d+)/$',
        'asset_detail',
        name="asset-detail"),

    url(r'^create/(?P<asset_id>\d+)/annotations/$',
        'annotation_create'),

    url(r'^create/(?P<asset_id>\d+)/global/$',
        'annotation_create_global'),

    url(r'^save/(?P<asset_id>\d+)/annotations/(?P<annot_id>\d+)/$',
        'annotation_save',
        name="annotation-save"),

    url(r'^delete/(?P<asset_id>\d+)/annotations/(?P<annot_id>\d+)/$',
        'annotation_delete',
        name="annotation-delete"),

    url(r'^delete/(?P<asset_id>\d+)/$',
        'asset_delete',
        name='asset-delete'),

    url(r'^xmeml/(?P<asset_id>\w+)/$',
        'final_cut_pro_xml',
        name="final_cut_pro_xml"),
)
