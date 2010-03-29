from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
import os.path

admin.autodiscover()

from projects import views as project
from assetmgr import views as asset
from mondrian_main import views as mondrian_main

import structuredcollaboration.urls

site_media_root = os.path.join(os.path.dirname(__file__),"media")
bookmarklet_root = os.path.join(os.path.dirname(__file__),"media","bookmarklets")

login_page = (r'^accounts/',include('django.contrib.auth.urls'))
if hasattr(settings,'WIND_BASE'):
    login_page = (r'^accounts/',include('djangowind.urls'))

redirect_after_logout = getattr(settings, 'LOGOUT_REDIRECT_URL', None)
urlpatterns = patterns('',
                       (r'^accounts/logout/$','django.contrib.auth.views.logout', 
                        {'next_page': redirect_after_logout}),
                       login_page,#see above

                       (r'^admin/', admin.site.urls),
                       (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': site_media_root}),
                       url(r'^bookmarklets/(?P<path>analyze.js)$', 'django.views.static.serve', {'document_root': bookmarklet_root}, name='analyze-bookmarklet'),
                       (r'^uploads/(?P<path>.*)$','django.views.static.serve',{'document_root' : settings.MEDIA_ROOT}),

                       ### Course-URLS ###
                       (r'^$', mondrian_main.class_portal),
                       #(r'^$','django.views.generic.simple.direct_to_template',{'template':'homepage.html'}),

                       url(r'^save/$', asset.add_view,
                           name="asset-save"),

                       (r'^asset/',include('mondrian.assetmgr.urls')),
                       (r'^annotations/',include('mondrian.djangosherd.urls')),
                       (r'^yourspace/',include('mondrian.mondrian_main.urls')),

                       #redundant, but for published projects/legacy
                       #(r'^project/',include('mondrian.projects.urls')),
                       #override/shortcut for published projects
                       url(r'^project/(?P<project_id>\d+)/[^v/]*$',
                           'projects.views.project_readonly_view',
                           name='project-view'
                           ),
                       (r'^explore/$','assetmgr.views.archive_explore'),
                       (r'^comments/', include('django.contrib.comments.urls')),

                       ### Public Access ###
                       
                       (r'', include(structuredcollaboration.urls)), #import at root
                       

)
