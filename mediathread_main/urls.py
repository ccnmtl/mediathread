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
    url(r'^(?P<user_name>\w[^/]*)/asset/$',
        'your_records',
        name='your-records'),
                       
    # User specific settings
    url(r'^(?P<user_name>\w[^/]*)/setting/$',
        'set_user_setting',
        name='set-user-setting'),
                       
    # Delete an asset from your collection
    # @todo - move this into asset. No reason for it to be here
    url(r'^(?P<user_name>\w[^/]*)/asset/(?P<asset_id>\d+)/$',
        'remove_record'),
)                       