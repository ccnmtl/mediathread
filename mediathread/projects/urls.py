from django.conf.urls import url
from mediathread.projects.views import (
    ProjectCreateView, ProjectDeleteView, ProjectSortView,
    SelectionAssignmentEditView, ProjectSaveView, ProjectDispatchView,
    UnsubmitResponseView, ProjectReadOnlyView, project_export_msword,
    project_export_html, project_revisions,
    SequenceAssignmentEditView)


urlpatterns = [
    url(r'^create/ja/$', SequenceAssignmentEditView.as_view(), {},
        name='sequence-assignment-create'),

    url(r'^edit/ja/(?P<project_id>\d+)/$',
        SequenceAssignmentEditView.as_view(), {},
        name='sequence-assignment-edit'),

    url(r'^create/sa/$', SelectionAssignmentEditView.as_view(), {},
        name='selection-assignment-create'),

    url(r'^edit/sa/(?P<project_id>\d+)/$',
        SelectionAssignmentEditView.as_view(), {},
        name='selection-assignment-edit'),

    url(r'^create/$', ProjectCreateView.as_view(), {}, "project-create"),

    url(r'^view/(?P<project_id>\d+)/$',
        ProjectDispatchView.as_view(), {}, name='project-workspace'),

    url(r'^view/(?P<project_id>\d+)/(?P<feedback>\w+)/$',
        ProjectDispatchView.as_view(), {}, name='project-workspace-feedback'),

    url(r'^save/(?P<project_id>\d+)/$',
        ProjectSaveView.as_view(), {},
        name='project-save'),

    url(r'^export/msword/(?P<project_id>\d+)/$',
        project_export_msword,
        name='project-export-msword'),

    url(r'^export/html/(?P<project_id>\d+)/$',
        project_export_html,
        name='project-export-html'),

    url(r'^delete/(?P<project_id>\d+)/$',
        ProjectDeleteView.as_view(), {}, 'project-delete'),

    url(r'^unsubmit/$',
        UnsubmitResponseView.as_view(), {}, 'unsubmit-response'),

    url(r'^revisions/(?P<project_id>\d+)/$',
        project_revisions,
        name='project-revisions'),

    # view versioned read only
    url(r'^view/(?P<project_id>\d+)/version/(?P<version_number>\d+)/$',
        ProjectReadOnlyView.as_view(),
        name='project-view-readonly'),

    # instructor information reorder
    url(r'^sort/$', ProjectSortView.as_view(), name='project-sort'),
]
