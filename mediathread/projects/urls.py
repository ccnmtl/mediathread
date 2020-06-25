from django.urls import path, include
from rest_framework import routers

from mediathread.projects.apiviews import ProjectSequenceAssetViewSet
from mediathread.projects.views import (
    ProjectCreateView, ProjectDeleteView, ProjectSortView,
    SelectionAssignmentEditView, ProjectSaveView, ProjectDispatchView,
    UnsubmitResponseView, ProjectReadOnlyView, project_export_msword,
    project_export_html, project_revisions,
    SequenceAssignmentEditView,
    UpdateVisibilityView
)


router = routers.DefaultRouter()
router.register(r'projectsequenceassets', ProjectSequenceAssetViewSet)


urlpatterns = [
    path('api/', include(router.urls)),
    path('create/ja/', SequenceAssignmentEditView.as_view(), {},
         name='sequence-assignment-create'),

    path('edit/ja/<int:project_id>/',
         SequenceAssignmentEditView.as_view(), {},
         name='sequence-assignment-edit'),

    path('create/sa/', SelectionAssignmentEditView.as_view(), {},
         name='selection-assignment-create'),

    path('edit/sa/<int:project_id>/',
         SelectionAssignmentEditView.as_view(), {},
         name='selection-assignment-edit'),

    path('create/', ProjectCreateView.as_view(), {}, "project-create"),

    path('view/<int:project_id>/',
         ProjectDispatchView.as_view(), {}, name='project-workspace'),

    path('view/<int:project_id>/<slug:feedback>/',
         ProjectDispatchView.as_view(), {}, name='project-workspace-feedback'),

    path('save/<int:project_id>/',
         ProjectSaveView.as_view(), {},
         name='project-save'),

    path('export/msword/<int:project_id>/',
         project_export_msword,
         name='project-export-msword'),

    path('export/html/<int:project_id>/',
         project_export_html,
         name='project-export-html'),

    path('delete/<int:project_id>/',
         ProjectDeleteView.as_view(), {}, 'project-delete'),

    path('unsubmit/',
         UnsubmitResponseView.as_view(), {}, 'unsubmit-response'),

    path('visibility/<int:project_id>/',
         UpdateVisibilityView.as_view(), {}, 'project-visibility'),

    path('revisions/<int:project_id>/',
         project_revisions,
         name='project-revisions'),

    # view versioned read only
    path('view/<int:project_id>/version/<int:version_number>/',
         ProjectReadOnlyView.as_view(),
         name='project-view-readonly'),

    # instructor information reorder
    path('sort/', ProjectSortView.as_view(), name='project-sort'),
]
