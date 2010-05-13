from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
import os.path

admin.autodiscover()

from projects import views as project
from assetmgr import views as asset
from mediathread_main import views as mediathread_main

import structuredcollaboration.urls

site_media_root = os.path.join(os.path.dirname(__file__),"media")
bookmarklet_root = os.path.join(os.path.dirname(__file__),"media","bookmarklets")

login_page = (r'^accounts/',include('django.contrib.auth.urls'))
if hasattr(settings,'WIND_BASE'):
    login_page = (r'^accounts/',include('djangowind.urls'))

redirect_after_logout = getattr(settings, 'LOGOUT_REDIRECT_URL', None)
urlpatterns = patterns('',
                       (r'^comments/', include('django.contrib.comments.urls')),
                       
                       (r'^accounts/logout/$','django.contrib.auth.views.logout', 
                        {'next_page': redirect_after_logout}),
                       login_page,#see above


                       (r'^admin/', admin.site.urls),
                       (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': site_media_root}),
                       url(r'^bookmarklets/(?P<path>analyze.js)$', 'django.views.static.serve', {'document_root': bookmarklet_root}, name='analyze-bookmarklet'),
                       url(r'^accounts/logged_in.js$', 'courseaffils.views.is_logged_in',
                           name='is_logged_in.js'),
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

                       ### Public Access ###
                       (r'', include(structuredcollaboration.urls)), #import at root
                       
)
