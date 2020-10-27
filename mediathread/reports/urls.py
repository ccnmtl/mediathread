from django.urls import path
from mediathread.reports.views import (
    SelfRegistrationReportView, ActivityByCourseView, ClassSummaryGraphView,
    AssignmentDetailReport, ClassSummaryView, ClassActivityView,
    ClassAssignmentsView, ClassAssignmentReport)


urlpatterns = [
    # urls prefix at root AND 'reports/'
    path('class_assignments/', ClassAssignmentsView.as_view(),
         name='class-assignments'),

    path('class_assignments/<int:project_id>/',
         ClassAssignmentReport.as_view(), name='class-assignment-report'),

    path('assignment/detail/<int:assignment_id>/',
         AssignmentDetailReport.as_view(), name='assignment-detail-report'),

    path('class_summary/', ClassSummaryView.as_view(), name='class-summary'),
    path('class_summary/graph.json', ClassSummaryGraphView.as_view(),
         name='class-summary-graph'),

    path('class_activity/', ClassActivityView.as_view(),
         name='class-activity'),

    path('activity/course/', ActivityByCourseView.as_view(),
         name="mediathread-activity-by-course"),

    path('self-registration/', SelfRegistrationReportView.as_view(),
         name="mediathread-self-registration")
]
