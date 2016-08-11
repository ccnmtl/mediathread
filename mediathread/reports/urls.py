from django.conf.urls import url

from mediathread.reports.views import SelfRegistrationReportView, \
    ActivityByCourseView, ClassSummaryGraphView, AssignmentDetailReport
from mediathread.reports.views import (
    class_assignments, class_assignment_report, class_summary,
    class_activity,
)

urlpatterns = [
    # urls prefix at root AND 'reports/'
    url(r'^class_assignments/$', class_assignments, name='class-assignments'),

    url(r'^class_assignments/(?P<project_id>\d+)/$',
        class_assignment_report, name='class-assignment-report'),

    url(r'^assignment/detail/(?P<assignment_id>\d+)/$',
        AssignmentDetailReport.as_view(), name='assignment-detail-report'),

    url(r'^class_summary/$', class_summary,
        name='class-summary'),
    url(r'^class_summary/graph.json$', ClassSummaryGraphView.as_view(),
        name='class-summary-graph'),

    url(r'^class_activity/$', class_activity,
        name='class-activity'),

    url(r'^activity/course/$', ActivityByCourseView.as_view(),
        name="mediathread-activity-by-course"),

    url(r'^self-registration/$', SelfRegistrationReportView.as_view(),
        name="mediathread-self-registration")
]
