import os.path

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import password_change, password_change_done, \
    password_reset, password_reset_done, password_reset_complete, \
    password_reset_confirm
from django.views.generic.base import TemplateView
from tastypie.api import Api

from mediathread.assetmgr.views import AssetCollectionView, AssetDetailView, \
    TagCollectionView
from mediathread.main.views import MigrateCourseView, MigrateMaterialsView, \
    RequestCourseView, ContactUsView
from mediathread.projects.views import ProjectCollectionView, ProjectDetailView
from mediathread.taxonomy.api import TermResource, VocabularyResource


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
admin_logout_page = (r'^accounts/logout/$',
                     'django.contrib.auth.views.logout',
                     {'next_page': '/admin/'})

if hasattr(settings, 'CAS_BASE'):
    auth_urls = (r'^accounts/', include('djangowind.urls'))
    logout_page = (r'^accounts/logout/$',
                   'djangowind.views.logout',
                   {'next_page': redirect_after_logout})
    admin_logout_page = (r'^admin/logout/$',
                         'djangowind.views.logout',
                         {'next_page': redirect_after_logout})


urlpatterns = patterns(
    '',

    (r'^$', 'mediathread.main.views.triple_homepage'),  # Homepage
    admin_logout_page,
    logout_page,
    (r'^admin/', admin.site.urls),

    # override the default urls for pasword
    url(r'^password/change/$',
        password_change,
        name='password_change'),
    url(r'^password/change/done/$',
        password_change_done,
        name='password_change_done'),
    url(r'^password/reset/$',
        password_reset,
        name='password_reset'),
    url(r'^password/reset/done/$',
        password_reset_done,
        name='password_reset_done'),
    url(r'^password/reset/complete/$',
        password_reset_complete,
        name='password_reset_complete'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        password_reset_confirm,
        name='password_reset_confirm'),

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

    url(r'^upgrade/', 'mediathread.main.views.upgrade_bookmarklet'),

    # Public Access ###
    (r'^s/', include('structuredcollaboration.urls')),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns(
        '',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
