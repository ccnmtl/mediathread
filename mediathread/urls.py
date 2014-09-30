from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import TemplateView
from mediathread.assetmgr.views import AssetCollectionView, AssetDetailView, \
    TagCollectionView
from mediathread.main.views import MigrateCourseView, MigrateMaterialsView, \
    RequestCourseView, ContactUsView
from mediathread.projects.views import ProjectCollectionView, ProjectDetailView
from mediathread.taxonomy.api import TermResource, VocabularyResource
from tastypie.api import Api
import os.path


tastypie_api = Api('')
tastypie_api.register(TermResource())
tastypie_api.register(VocabularyResource())

admin.autodiscover()

bookmarklet_root = os.path.join(os.path.dirname(__file__),
                                "../media/",
                                "bookmarklets")

redirect_after_logout = getattr(settings, 'LOGOUT_REDIRECT_URL', None)

auth_urls = (r'^accounts/', include('django.contrib.auth.urls'))
logout_page = (r'^accounts/logout/$',
               'django.contrib.auth.views.logout',
               {'next_page': redirect_after_logout})

if hasattr(settings, 'WIND_BASE'):
    auth_urls = (r'^accounts/', include('djangowind.urls'))
    logout_page = (r'^accounts/logout/$', 'djangowind.views.logout',
                   {'next_page': redirect_after_logout})


urlpatterns = patterns(
    '',

    (r'^$', 'mediathread.main.views.triple_homepage'),  # Homepage

    (r'^admin/', admin.site.urls),

    # API - JSON rendering layers. Half hand-written, half-straight tasty=pie
    (r'^api/asset/user/(?P<record_owner_name>\w[^/]*)/$',
     AssetCollectionView.as_view(), {}, 'assets-by-user'),
    (r'^api/asset/(?P<asset_id>\d+)/$', AssetDetailView.as_view(),
     {}, 'asset-detail'),
    (r'^api/asset/$', AssetCollectionView.as_view(), {}, 'assets-by-course'),
    url(r'^api/user/courses$', 'courseaffils.views.course_list_query',
        name='api-user-courses'),
    (r'^api/tag/$', TagCollectionView.as_view(), {}),
    (r'^api/project/user/(?P<record_owner_name>\w[^/]*)/$',
     ProjectCollectionView.as_view(), {}, 'project-by-user'),
    (r'^api/project/(?P<project_id>\d+)/$', ProjectDetailView.as_view(),
     {}, 'asset-detail'),
    (r'^api/project/$', ProjectCollectionView.as_view(), {}),
    (r'^api', include(tastypie_api.urls)),

    # Collections Space
    (r'^asset/', include('mediathread.assetmgr.urls')),

    auth_urls,  # see above

    # Bookmarklet + cache defeating
    url(r'^bookmarklets/(?P<path>analyze.js)$', 'django.views.static.serve',
        {'document_root': bookmarklet_root}, name='analyze-bookmarklet'),
    url(r'^nocache/\w+/bookmarklets/(?P<path>analyze.js)$',
        'django.views.static.serve', {'document_root': bookmarklet_root},
        name='nocache-analyze-bookmarklet'),

    (r'^comments/', include('django.contrib.comments.urls')),

    # Columbia only request forms.
    (r'^contact/success/$',
     TemplateView.as_view(template_name="main/contact_success.html")),
    (r'^contact/$', ContactUsView.as_view()),
    (r'^course/request/success/$',
     TemplateView.as_view(template_name="main/course_request_success.html")),
    (r'^course/request/', RequestCourseView.as_view()),

    # Courseaffils
    url(r'^accounts/logged_in.js$', 'courseaffils.views.is_logged_in',
        name='is_logged_in.js'),
    url(r'^nocache/\w+/accounts/logged_in.js$',
        'courseaffils.views.is_logged_in', name='nocache-is_logged_in.js'),

    (r'^crossdomain.xml$', 'django.views.static.serve',
     {'document_root': os.path.abspath(os.path.dirname(__file__)),
      'path': 'crossdomain.xml'}),

    url(r'^dashboard/migrate/materials/(?P<course_id>\d+)/$',
        MigrateMaterialsView.as_view(), {}, 'dashboard-migrate-materials'),
    url(r'^dashboard/migrate/$', MigrateCourseView.as_view(),
        {}, "dashboard-migrate"),
    url(r'^dashboard/sources/',
        'mediathread.main.views.class_manage_sources',
        name="class-manage-sources"),
    url(r'^dashboard/settings/',
        'mediathread.main.views.class_settings',
        name="class-settings"),

    # Discussion
    (r'^discussion/', include('mediathread.discussions.urls')),

    # Manage Sources
    url(r'^explore/redirect/$',
        'mediathread.assetmgr.views.source_redirect',
        name="source_redirect"),

    (r'^jsi18n', 'django.views.i18n.javascript_catalog'),

    logout_page,

    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root':
      os.path.abspath(os.path.join(os.path.dirname(admin.__file__), 'media')),
      'show_indexes': True}),

    # Composition Space
    (r'^project/', include('mediathread.projects.urls')),

    # Instructor Dashboard & reporting
    (r'^reports/', include('mediathread.reports.urls')),

    # Bookmarklet Entry point
    # Staff custom asset entry
    url(r'^save/$',
        'mediathread.assetmgr.views.asset_create',
        name="asset-save"),

    (r'^setting/(?P<user_name>\w[^/]*)/$',
     'mediathread.main.views.set_user_setting'),

    (r'^stats/', TemplateView.as_view(template_name="stats.html")),
    (r'^smoketest/', include('smoketest.urls')),

    url(r'^taxonomy/', include('mediathread.taxonomy.urls')),

    url(r'^upgrade/', TemplateView.as_view(
        template_name="assetmgr/upgrade_bookmarklet.html")),

    ### Public Access ###
    (r'^s/', include('structuredcollaboration.urls')),
)
