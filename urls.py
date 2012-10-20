from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
import os.path


admin.autodiscover()

site_media_root = os.path.join(os.path.dirname(__file__),"media")
bookmarklet_root = os.path.join(os.path.dirname(__file__),"media","bookmarklets")

redirect_after_logout = getattr(settings, 'LOGOUT_REDIRECT_URL', None)

auth_urls = (r'^accounts/',include('django.contrib.auth.urls'))
logout_page = (r'^accounts/logout/$','django.contrib.auth.views.logout', {'next_page': redirect_after_logout})

if hasattr(settings,'WIND_BASE'):
    auth_urls = (r'^accounts/',include('djangowind.urls'))
    logout_page = (r'^accounts/logout/$','djangowind.views.logout', {'next_page': redirect_after_logout})

urlpatterns = patterns('',
                       (r'^crossdomain.xml$', 'django.views.static.serve', {'document_root': os.path.abspath(os.path.dirname(__file__))
, 'path': 'crossdomain.xml'}),
                       (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
                           {'document_root': os.path.abspath(os.path.join(os.path.dirname(admin.__file__), 'media')),'show_indexes': True}),
                           
                       (r'^comments/', include('django.contrib.comments.urls')),
                       
                       logout_page,
                       
                       auth_urls,#see above
                                              
                       (r'^contact/', login_required(direct_to_template), {'template': 'mediathread_main/contact.html'}),
                        
                       (r'^_stats/', direct_to_template, {'template': 'mediathread_main/stats.html'}),
                       (r'^admin/', admin.site.urls),
                       (r'^jsi18n', 'django.views.i18n.javascript_catalog'),
                       (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': site_media_root}),
                       url(r'^bookmarklets/(?P<path>analyze.js)$', 'django.views.static.serve', {'document_root': bookmarklet_root}, name='analyze-bookmarklet'),
                       ## one for cache defeating
                       url(r'^nocache/\w+/bookmarklets/(?P<path>analyze.js)$', 'django.views.static.serve', {'document_root': bookmarklet_root}, name='nocache-analyze-bookmarklet'),
                       
                       # Courseafills
                       url(r'^accounts/logged_in.js$', 'courseaffils.views.is_logged_in',
                           name='is_logged_in.js'),
                       url(r'^nocache/\w+/accounts/logged_in.js$', 'courseaffils.views.is_logged_in',
                           name='nocache-is_logged_in.js'),
                       url(r'^api/user/courses$', 'courseaffils.views.course_list_query',
                           name='api-user-courses'),
                       (r'^uploads/(?P<path>.*)$','django.views.static.serve',{'document_root' : settings.MEDIA_ROOT}),

                       # Homepage
                       (r'^$', 'mediathread_main.views.triple_homepage'),
                       (r'^yourspace/', include('mediathread.mediathread_main.urls')), 
                    
                       # Instructor Dashboard & reporting
                       (r'^reports/',include('mediathread.reports.urls')),
                       url(r'^dashboard/addsource/', 'mediathread_main.views.class_addsource', name="class-add-source"),
                       url(r'^dashboard/settings/', 'mediathread_main.views.class_settings', name="class-settings"),
                       url(r'^dashboard/$', 'mediathread_main.views.dashboard', name="dashboard-home"),
                       
                       # Recent Activity
                       url(r'^notifications/$','mediathread_main.views.notifications', name="notifications"),
                       
                       # Collections Space
                       (r'^asset/', include('mediathread.assetmgr.urls')),
                       (r'^annotations/', include('mediathread.djangosherd.urls')),
                       
                       # Bookmarklet Entry point
                       # Staff custom asset entry
                       url(r'^save/$', 'assetmgr.views.asset_create', name="asset-save"),
                       
                       # Composition Space
                       (r'^project/',include('mediathread.projects.urls')),
                       
                       # Discussion
                       (r'^discussion/',include('mediathread.discussions.urls')),
                       
                       # Manage Sources
                       url(r'^explore/$','assetmgr.views.browse_sources', name="explore"),
                       url(r'^explore/redirect/$','assetmgr.views.source_redirect', name="source_redirect"),
                       
                       ### Public Access ###
                       (r'', include('structuredcollaboration.urls')), #import at root
)
