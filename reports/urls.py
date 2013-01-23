from django.conf.urls.defaults import patterns, url


urlpatterns = patterns(
    '',
    # urls prefix at root AND 'reports/'

    url(r'^class_assignments/$',
        'reports.views.class_assignments',
        name="class-assignments"),
    url(r'^class_assignments/(?P<id>\d+)/$',
        'reports.views.class_assignment_report',
        name="class-assignment-report"),

    url(r'^class_summary/$', 'reports.views.class_summary',
        name="class-summary"),
    url(r'^class_summary/graph.json$',
        'reports.views.class_summary_graph',
        name="class-summary-graph"),

    url(r'^class_activity/$', 'reports.views.class_activity',
        name="class-activity"),

    url(r'^activity/course/$',
        'reports.views.mediathread_activity_by_course',
        name="mediathread-activity-by-course"),
    url(r'^activity/school/$',
        'reports.views.mediathread_activity_by_school',
        name="mediathread-activity-by-school"),

)
