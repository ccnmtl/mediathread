from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
import os.path

admin.autodiscover()

from projects import views as project
from assetmgr import views as asset
from mediathread_main import views as mediathread_main

import structuredcollaboration.urls
#import slider.urls

site_media_root = os.path.join(os.path.dirname(__file__),"media")
bookmarklet_root = os.path.join(os.path.dirname(__file__),"media","bookmarklets")

redirect_after_logout = getattr(settings, 'LOGOUT_REDIRECT_URL', None)

auth_urls = (r'^accounts/',include('django.contrib.auth.urls'))
logout_page = (r'^accounts/logout/$','django.contrib.auth.views.logout', {'next_page': redirect_after_logout})
if hasattr(settings,'WIND_BASE'):
    auth_urls = (r'^accounts/',include('djangowind.urls'))
    logout_page = (r'^accounts/logout/$','djangowind.views.logout', {'next_page': redirect_after_logout})

urlpatterns = patterns('',
                       (r'^comments/', include('django.contrib.comments.urls')),
                       logout_page,
                       auth_urls,#see above


                       (r'^admin/', admin.site.urls),
                       (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': site_media_root}),
                       url(r'^bookmarklets/(?P<path>analyze.js)$', 'django.views.static.serve', {'document_root': bookmarklet_root}, name='analyze-bookmarklet'),
                       ## one for cache defeating
                       url(r'^nocache/\w+/bookmarklets/(?P<path>analyze.js)$', 'django.views.static.serve', {'document_root': bookmarklet_root}, name='nocache-analyze-bookmarklet'),
                       url(r'^accounts/logged_in.js$', 'courseaffils.views.is_logged_in',
                           name='is_logged_in.js'),
                       url(r'^nocache/\w+/accounts/logged_in.js$', 'courseaffils.views.is_logged_in',
                           name='nocache-is_logged_in.js'),
                       (r'^uploads/(?P<path>.*)$','django.views.static.serve',{'document_root' : settings.MEDIA_ROOT}),

                       ### Course-URLS ###
                       (r'^$', mediathread_main.class_portal),
                       #(r'^$','django.views.generic.simple.direct_to_template',{'template':'homepage.html'}),

                       url(r'^save/$', asset.add_view,
                           name="asset-save"),

                       (r'^asset/',include('mediathread.assetmgr.urls')),
                       (r'^annotations/',include('mediathread.djangosherd.urls')),
                       (r'^yourspace/',include('mediathread.mediathread_main.urls')),
                       
                       #redundant, but for published projects/legacy
                       #(r'^project/',include('mediathread.projects.urls')),
                       #override/shortcut for published projects
                       url(r'^project/(?P<project_id>\d+)/[^v/]*$',
                           'projects.views.project_readonly_view',
                           name='project-view'
                           ),
                       (r'^explore/$','assetmgr.views.archive_explore'),

                       #threaded discussion:
                       (r'^discussion/',include('mediathread.discussions.urls')),

                       #(r'', include(slider.urls)),
 
                       ### Public Access ###
                       (r'', include(structuredcollaboration.urls)), #import at root
                       
)
