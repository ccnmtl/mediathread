from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns(
    'mediathread_main.views',
    #urls prefix at root AND 'yourspace/' 
                           
    url(r'^all/asset/$',
        'all_records',
        name='all-records'),

    url(r'^(?P<user_name>\w[^/]*)/asset/$',
        'your_records',
        name='your-records'),

)                       