from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns(
    '',
    #urls prefix at root AND 'reports/' 

    url(r'^class_assignments/$',
        'reports.views.class_assignments',
        name="class-assignments"),
    url(r'^class_assignments/(?P<id>\d+)/$',
        'reports.views.class_assignment_report',
        name="class-assignment-report"),
    
    url(r'^class_summary/$','reports.views.class_summary',
        name="class-summary"),
    url(r'^class_summary/graph.json$',
        'reports.views.class_summary_graph',
        name="class-summary-graph"),
    
    url(r'^class_activity/$','reports.views.class_activity',
        name="class-activity"),
    )

