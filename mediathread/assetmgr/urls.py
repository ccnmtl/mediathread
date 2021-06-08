import os.path

from django.urls import path

from mediathread.assetmgr.views import (
    AssetWorkspaceView, AssetReferenceView, ManageExternalCollectionView,
    AssetEmbedView, AssetEmbedListView, ScalarExportView,
    MostRecentView, annotation_create, annotation_create_global,
    annotation_save, annotation_delete, asset_delete, final_cut_pro_xml,
    AnnotationCopyView, PDFViewerDetailView
)
from mediathread.djangosherd.apiviews import SherdNoteCreate
from mediathread.assetmgr.apiviews import AssetUpdate


media_root = os.path.join(os.path.dirname(__file__), 'media')

urlpatterns = [
    # Archive save or delete
    path('archive/',
         ManageExternalCollectionView.as_view(), {},
         'collection-add-or-remove'),

    # Archive save or delete
    path('references/<int:asset_id>/', AssetReferenceView.as_view(),
         {}, 'asset-references'),

    # Goto the most recently created asset by user
    path('most_recent/', MostRecentView.as_view(), name='asset-most-recent'),

    path('<int:asset_id>/', AssetWorkspaceView.as_view(),
         {}, 'asset-view'),

    path('<int:asset_id>/annotations/<int:annot_id>/',
         AssetWorkspaceView.as_view(), {}, 'annotation-view'),

    path('create/<int:asset_id>/annotations/', annotation_create),

    # django-rest-framework
    path('<int:asset_id>/sherdnote/create/',
         SherdNoteCreate.as_view(),
         name='sherdnote-create'),

    path('<int:asset_id>/save/',
         AssetUpdate.as_view(),
         name='asset-update'),

    path('create/<int:asset_id>/global/', annotation_create_global),

    path('copy/<int:asset_id>/annotations/<int:annot_id>/',
         AnnotationCopyView.as_view(), {}, 'annotation-copy-view'),

    path('save/<int:asset_id>/annotations/<int:annot_id>/',
         annotation_save,
         name="annotation-save"),

    path('delete/<int:asset_id>/annotations/<int:annot_id>/',
         annotation_delete,
         name="annotation-delete"),

    path('delete/<int:asset_id>/', asset_delete, name='asset-delete'),

    path('xmeml/<int:asset_id>/',
         final_cut_pro_xml,
         name="final_cut_pro_xml"),

    path('embed/view/<int:course_id>/<int:annot_id>/',
         AssetEmbedView.as_view(), {}, 'selection-embed-view'),

    path('embed/', AssetEmbedListView.as_view(), {}, 'asset-embed-list'),

    path('scalar/', ScalarExportView.as_view(), name='scalar_export'),

    path('pdfjs/<int:pk>/', PDFViewerDetailView.as_view(), {},
         name='pdfjs'),

    # Asset workspace variations
    path('', AssetWorkspaceView.as_view(), {}, 'asset-collection-view'),
]
