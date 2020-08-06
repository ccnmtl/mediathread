from django.urls import path, include
from mediathread.projects.apiviews import ProjectSequenceAssetViewSet
from mediathread.projects.views import (
    ProjectCreateView, ProjectDeleteView, ProjectSortView,
    SelectionAssignmentEditView, ProjectSaveView, ProjectDispatchView,
    UnsubmitResponseView, ProjectReadOnlyView,
    ProjectExportWord, ProjectPrintView,
    SequenceAssignmentEditView, CompositionAssignmentEditView,
    CompositionAssignmentResponseView, UpdateVisibilityView,
    DiscussionAssignmentWizardView, DiscussionAssignmentCreateView,
    DiscussionAssignmentSaveView, ProjectVersionListView
)
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'projectsequenceassets', ProjectSequenceAssetViewSet)


urlpatterns = [
    path('api/', include(router.urls)),

    path('create/ca/', CompositionAssignmentEditView.as_view(), {},
         name='composition-assignment-create'),

    path('edit/ca/<int:project_id>/',
         CompositionAssignmentEditView.as_view(), {},
         name='composition-assignment-edit'),

    path('wizard/create/da/', DiscussionAssignmentWizardView.as_view(), {},
         name='discussion-assignment-create-wizard'),

    path('wizard/edit/da/<int:project_id>/',
         DiscussionAssignmentWizardView.as_view(), {},
         name='discussion-assignment-edit-wizard'),

    path('create/da/',
         DiscussionAssignmentCreateView.as_view(), {},
         "discussion-assignment-create"),

    path('save/da/<int:project_id>',
         DiscussionAssignmentSaveView.as_view(), {},
         "discussion-assignment-save"),

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

    path('response/<int:project_id>/',
         CompositionAssignmentResponseView.as_view(), {},
         name='assignment-response-view'),

    path('save/<int:project_id>/',
         ProjectSaveView.as_view(), {},
         name='project-save'),

    path('export/msword/<int:project_id>/',
         ProjectExportWord.as_view(),
         name='project-export-msword'),

    path('print/<int:project_id>/',
         ProjectPrintView.as_view(),
         name='project-print-html'),

    path('delete/<int:project_id>/',
         ProjectDeleteView.as_view(), {}, 'project-delete'),

    path('unsubmit/',
         UnsubmitResponseView.as_view(), {}, 'unsubmit-response'),

    path('visibility/<int:project_id>/',
         UpdateVisibilityView.as_view(), {}, 'project-visibility'),

    # view versioned read only
    path('<int:project_id>/version/<int:version_number>/',
         ProjectReadOnlyView.as_view(),
         name='project-view-readonly'),

    path('<int:project_id>/version/',
         ProjectVersionListView.as_view(),
         name='project-revisions'),

    # instructor information reorder
    path('sort/', ProjectSortView.as_view(), name='project-sort'),
]
