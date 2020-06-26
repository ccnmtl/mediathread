from django.urls import path

from mediathread.reports.views import SelfRegistrationReportView, \
    ActivityByCourseView, ClassSummaryGraphView, AssignmentDetailReport
from mediathread.reports.views import (
    class_assignments, class_assignment_report, class_summary,
    class_activity,
)

urlpatterns = [
    # urls prefix at root AND 'reports/'
    path('class_assignments/', class_assignments, name='class-assignments'),

    path('class_assignments/<int:project_id>/',
         class_assignment_report, name='class-assignment-report'),

    path('assignment/detail/<int:assignment_id>/',
         AssignmentDetailReport.as_view(), name='assignment-detail-report'),

    path('class_summary/', class_summary,
         name='class-summary'),
    path('class_summary/graph.json', ClassSummaryGraphView.as_view(),
         name='class-summary-graph'),

    path('class_activity/', class_activity,
         name='class-activity'),

    path('activity/course/', ActivityByCourseView.as_view(),
         name="mediathread-activity-by-course"),

    path('self-registration/', SelfRegistrationReportView.as_view(),
         name="mediathread-self-registration")
]
