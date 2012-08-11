from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns(
    'mediathread_main.views',
    # urls prefix 'yourspace/' 
                      
    # Collections box: View All Class Members' assets & work     
    url(r'^all/asset/$',
        'all_records',
        name='all-records'),

    # Collections box: View a specified class member's assets & work
    url(r'^(?P<record_owner_name>\w[^/]*)/asset/$',
        'your_records',
        name='your-records'),
                       
    # User specific settings -- primarily used to track help visibility
    url(r'^(?P<user_name>\w[^/]*)/setting/$',
        'set_user_setting',
        name='set-user-setting'),                       
)                       