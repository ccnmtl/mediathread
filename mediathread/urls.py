import os.path

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import (password_change, password_change_done,
                                       password_reset, password_reset_done,
                                       password_reset_complete,
                                       password_reset_confirm)
from django.views.generic.base import TemplateView
from registration.backends.default.views import RegistrationView
from tastypie.api import Api

from mediathread.assetmgr.views import (
    AssetCollectionView, AssetDetailView, TagCollectionView,
    RedirectToExternalCollectionView, RedirectToUploaderView,
    AssetCreateView, BookmarkletMigrationView)
from mediathread.main.forms import CustomRegistrationForm
from mediathread.main.views import (
    MethCourseListView, AffilActivateView,
    ContactUsView, RequestCourseView, IsLoggedInView, IsLoggedInDataView,
    MigrateMaterialsView, MigrateCourseView, CourseManageSourcesView,
    CourseSettingsView, CourseDeleteMaterialsView, course_detail_view,
    CourseRosterView, CoursePromoteUserView, CourseDemoteUserView,
    CourseRemoveUserView, CourseAddUserByUNIView,
    CourseInviteUserByEmailView, CourseAcceptInvitationView, ClearTestCache)
from mediathread.projects.views import (
    ProjectCollectionView, ProjectDetailView, ProjectItemView,
    ProjectPublicView)
from mediathread.taxonomy.api import TermResource, VocabularyResource


tastypie_api = Api('')
tastypie_api.register(TermResource())
tastypie_api.register(VocabularyResource())

admin.autodiscover()

bookmarklet_root = os.path.join(os.path.dirname(__file__),
                                '../media/',
                                'bookmarklets')

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

    url(r'^$', course_detail_view, name='home'),
    admin_logout_page,
    logout_page,
    (r'^admin/', admin.site.urls),

    # override the default urls for password
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

    url(r'^accounts/invite/accept/(?P<uidb64>[0-9A-Za-z]+)',
        CourseAcceptInvitationView.as_view(),
        name='course-invite-accept'),
    url(r'^accounts/invite/complete/', TemplateView.as_view(
        template_name='registration/invitation_activate_complete.html'),
        name='course-invite-complete'),

    url(r'^accounts/register/$',
        RegistrationView.as_view(form_class=CustomRegistrationForm),
        name='registration_register'),
    (r'^accounts/', include('registration.backends.default.urls')),

    # API - JSON rendering layers. Half hand-written, half-straight tasty=pie
    (r'^api/asset/user/(?P<record_owner_name>\w[^/]*)/$',
     AssetCollectionView.as_view(), {}, 'assets-by-user'),
    (r'^api/asset/(?P<asset_id>\d+)/$', AssetDetailView.as_view(),
     {}, 'asset-detail'),
    (r'^api/asset/$', AssetCollectionView.as_view(), {}, 'assets-by-course'),
    url(r'^api/user/courses$', 'courseaffils.views.course_list_query',
        name='api-user-courses'),
    (r'^api/tag/$', TagCollectionView.as_view(), {}, 'tag-collection-view'),
    (r'^api/project/user/(?P<record_owner_name>\w[^/]*)/$',
     ProjectCollectionView.as_view(), {}, 'project-by-user'),
    (r'^api/project/(?P<project_id>\d+)/(?P<asset_id>\d+)/$',
     ProjectItemView.as_view(), {}, 'project-item-view'),
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

    (r'^comments/', include('django_comments.urls')),

    # Contact us forms.
    (r'^contact/success/$',
     TemplateView.as_view(template_name='main/contact_success.html')),
    (r'^contact/$', ContactUsView.as_view()),
    (r'^course/request/success/$',
     TemplateView.as_view(template_name='main/course_request_success.html')),
    (r'^course/request/', RequestCourseView.as_view()),
    url(r'^affil/(?P<pk>\d+)/activate/$',
        AffilActivateView.as_view(),
        name='affil_activate'),
    url(r'^course/list/$',
        MethCourseListView.as_view(),
        name='course_list'),

    # Bookmarklet
    url(r'^accounts/logged_in.js$', IsLoggedInView.as_view(), {},
        name='is_logged_in.js'),
    url(r'^accounts/is_logged_in/$', IsLoggedInDataView.as_view(), {},
        name='is_logged_in'),
    url(r'^bookmarklet_migration/$', BookmarkletMigrationView.as_view(), {},
        name='bookmarklet_migration'),
    url(r'^upgrade/', 'mediathread.assetmgr.views.upgrade_bookmarklet',
        name='bookmarklet_upgrade'),

    (r'^crossdomain.xml$', 'django.views.static.serve',
     {'document_root': os.path.abspath(os.path.dirname(__file__)),
      'path': 'crossdomain.xml'}),

    url(r'^dashboard/migrate/materials/(?P<course_id>\d+)/$',
        MigrateMaterialsView.as_view(), {}, 'dashboard-migrate-materials'),
    url(r'^dashboard/migrate/$', MigrateCourseView.as_view(),
        {}, 'dashboard-migrate'),
    url(r'^dashboard/roster/promote/', CoursePromoteUserView.as_view(),
        name='course-roster-promote'),
    url(r'^dashboard/roster/demote/', CourseDemoteUserView.as_view(),
        name='course-roster-demote'),
    url(r'^dashboard/roster/remove/', CourseRemoveUserView.as_view(),
        name='course-roster-remove'),
    url(r'^dashboard/roster/add/uni/', CourseAddUserByUNIView.as_view(),
        name='course-roster-add-uni'),
    url(r'^dashboard/roster/add/email/', CourseInviteUserByEmailView.as_view(),
        name='course-roster-invite-email'),
    url(r'^dashboard/roster/', CourseRosterView.as_view(),
        name='course-roster'),

    url(r'^dashboard/sources/', CourseManageSourcesView.as_view(),
        name='class-manage-sources'),
    url(r'^dashboard/settings/', CourseSettingsView.as_view(),
        name='course-settings'),
    url(r'^dashboard/delete/materials/', CourseDeleteMaterialsView.as_view(),
        name='course-delete-materials'),

    # Discussion
    (r'^discussion/', include('mediathread.discussions.urls')),

    # External Collections
    url(r'^explore/redirect/(?P<collection_id>\d+)/$',
        RedirectToExternalCollectionView.as_view(),
        name='collection_redirect'),

    # Uploader
    url(r'^upload/redirect/(?P<collection_id>\d+)/$',
        RedirectToUploaderView.as_view(),
        name='uploader_redirect'),

    url(r'^impersonate/', include('impersonate.urls')),

    (r'^jsi18n', 'django.views.i18n.javascript_catalog'),

    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root':
      os.path.abspath(os.path.join(os.path.dirname(admin.__file__), 'media')),
      'show_indexes': True}),

    # Composition Space
    (r'^project/', include('mediathread.projects.urls')),

    # Instructor Dashboard & reporting
    (r'^reports/', include('mediathread.reports.urls')),

    # Bookmarklet, Wardenclyffe, Staff custom asset entry
    url(r'^save/$', AssetCreateView.as_view(), name='asset-save'),

    (r'^setting/(?P<user_name>\w[^/]*)/$',
     'mediathread.main.views.set_user_setting'),

    (r'^stats/', TemplateView.as_view(template_name='stats.html')),
    (r'^smoketest/', include('smoketest.urls')),

    url(r'^taxonomy/', include('mediathread.taxonomy.urls')),

    (r'^lti/', include('lti_auth.urls')),

    (r'^test/clear/', ClearTestCache.as_view()),

    # Public To World Access ###
    url(r'^s/(?P<context_slug>\w+)/(?P<obj_type>\w+)/(?P<obj_id>\d+)/',
        ProjectPublicView.as_view(), name='collaboration-obj-view'),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns(
        '',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
