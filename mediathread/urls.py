import os.path

import courseaffils
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import (password_change, password_change_done,
                                       password_reset, password_reset_done,
                                       password_reset_complete,
                                       password_reset_confirm)
import django.contrib.auth.views
from django.views.generic.base import TemplateView
import django.views.i18n
import django.views.static
import djangowind.views
from registration.backends.default.views import RegistrationView
from tastypie.api import Api

from mediathread.api import CourseResource
from mediathread.assetmgr.views import (
    AssetCollectionView, AssetDetailView, TagCollectionView,
    RedirectToExternalCollectionView, RedirectToUploaderView,
    AssetCreateView, BookmarkletMigrationView, AssetUpdateView)
from mediathread.main.forms import CustomRegistrationForm
from mediathread.main.views import (
    error_500,
    MethCourseListView, AffilActivateView,
    InstructorDashboardSettingsView,
    ContactUsView, IsLoggedInView, IsLoggedInDataView,
    MigrateMaterialsView, MigrateCourseView, CourseManageSourcesView,
    CourseDeleteMaterialsView, CourseDetailView, course_detail_view,
    CourseRosterView, CoursePromoteUserView, CourseDemoteUserView,
    CourseRemoveUserView, CourseAddUserByUNIView,
    CourseInviteUserByEmailView, CourseAcceptInvitationView, ClearTestCache,
    CourseResendInviteView, set_user_setting,
    LTICourseSelector, LTICourseCreate
)
from mediathread.projects.views import (
    ProjectCollectionView, ProjectDetailView, ProjectItemView,
    ProjectPublicView)
from mediathread.taxonomy.api import TermResource, VocabularyResource


tastypie_api = Api('')
tastypie_api.register(TermResource())
tastypie_api.register(VocabularyResource())
tastypie_api.register(CourseResource())

admin.autodiscover()

bookmarklet_root = os.path.join(os.path.dirname(__file__),
                                '../media/',
                                'bookmarklets')

redirect_after_logout = getattr(settings, 'LOGOUT_REDIRECT_URL', None)

auth_urls = url(r'^accounts/', include('django.contrib.auth.urls'))

logout_page = url(r'^accounts/logout/$',
                  django.contrib.auth.views.logout,
                  {'next_page': redirect_after_logout})
admin_logout_page = url(r'^accounts/logout/$',
                        django.contrib.auth.views.logout,
                        {'next_page': '/admin/'})

if hasattr(settings, 'CAS_BASE'):
    auth_urls = url(r'^accounts/', include('djangowind.urls'))
    logout_page = url(r'^accounts/logout/$',
                      djangowind.views.logout,
                      {'next_page': redirect_after_logout})
    admin_logout_page = url(r'^admin/logout/$',
                            djangowind.views.logout,
                            {'next_page': redirect_after_logout})


urlpatterns = [
    url(r'^$', course_detail_view, name='home'),
    url(r'^500$', error_500, name='error_500'),
    admin_logout_page,
    logout_page,
    url(r'^admin/', admin.site.urls),

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

    url(r'^accounts/invite/accept/(?P<uidb64>[0-9A-Za-z-]+)/$',
        CourseAcceptInvitationView.as_view(),
        name='course-invite-accept'),
    url(r'^accounts/invite/complete/', TemplateView.as_view(
        template_name='registration/invitation_complete.html'),
        name='course-invite-complete'),

    url(r'^accounts/register/$',
        RegistrationView.as_view(form_class=CustomRegistrationForm),
        name='registration_register'),
    url(r'^accounts/', include('registration.backends.default.urls')),

    # API - JSON rendering layers. Half hand-written, half-straight tasty=pie
    url(r'^api/asset/user/(?P<record_owner_name>\w[^/]*)/$',
        AssetCollectionView.as_view(), {}, 'assets-by-user'),
    url(r'^api/asset/(?P<asset_id>\d+)/$', AssetDetailView.as_view(),
        {}, 'asset-detail'),
    url(r'^api/asset/$', AssetCollectionView.as_view(), {},
        'assets-by-course'),
    url(r'^api/user/courses$', courseaffils.views.course_list_query,
        name='api-user-courses'),
    url(r'^api/tag/$', TagCollectionView.as_view(), {}, 'tag-collection-view'),
    url(r'^api/project/user/(?P<record_owner_name>\w[^/]*)/$',
        ProjectCollectionView.as_view(), {}, 'project-by-user'),
    url(r'^api/project/(?P<project_id>\d+)/(?P<asset_id>\d+)/$',
        ProjectItemView.as_view(), {}, 'project-item-view'),
    url(r'^api/project/(?P<project_id>\d+)/$', ProjectDetailView.as_view(),
        {}, 'asset-detail'),
    url(r'^api/project/$', ProjectCollectionView.as_view(), {}),
    url(r'^api', include(tastypie_api.urls)),

    # Collections Space
    url(r'^asset/', include('mediathread.assetmgr.urls')),

    url(r'^sequence/', include('mediathread.sequence.urls')),

    auth_urls,  # see above

    # Bookmarklet + cache defeating
    url(r'^bookmarklets/(?P<path>analyze.js)$', django.views.static.serve,
        {'document_root': bookmarklet_root}, name='analyze-bookmarklet'),
    url(r'^nocache/\w+/bookmarklets/(?P<path>analyze.js)$',
        django.views.static.serve, {'document_root': bookmarklet_root},
        name='nocache-analyze-bookmarklet'),

    url(r'^comments/', include('django_comments.urls')),

    # Contact us forms.
    url(r'^contact/success/$',
        TemplateView.as_view(template_name='main/contact_success.html')),
    url(r'^contact/$', ContactUsView.as_view()),
    url(r'^course/request/success/$', TemplateView.as_view(
        template_name='main/course_request_success.html')),
    url(r'^affil/(?P<pk>\d+)/activate/$',
        AffilActivateView.as_view(),
        name='affil_activate'),

    url(r'^course/(?P<pk>\d+)/$', CourseDetailView.as_view(),
        name='course_detail'),

    url(r'^course/list/$',
        MethCourseListView.as_view(),
        name='course_list'),
    url(r'^course/lti/create/$',
        LTICourseCreate.as_view(), name='lti-course-create'),
    url(r'^course/lti/(?P<context>\w[^/]*)/$',
        LTICourseSelector.as_view(), name='lti-course-select'),

    # Bookmarklet
    url(r'^accounts/logged_in.js$', IsLoggedInView.as_view(), {},
        name='is_logged_in.js'),
    url(r'^accounts/is_logged_in/$', IsLoggedInDataView.as_view(), {},
        name='is_logged_in'),
    url(r'^bookmarklet_migration/$', BookmarkletMigrationView.as_view(), {},
        name='bookmarklet_migration'),

    url(r'^crossdomain.xml$', django.views.static.serve, {
        'document_root': os.path.join(os.path.dirname(__file__), '../media/'),
        'path': 'crossdomain.xml'
    }),

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
    url(r'^dashboard/roster/resend/email/', CourseResendInviteView.as_view(),
        name='course-roster-resend-email'),
    url(r'^dashboard/roster/', CourseRosterView.as_view(),
        name='course-roster'),

    url(r'^dashboard/sources/', CourseManageSourcesView.as_view(),
        name='class-manage-sources'),
    url(r'^dashboard/delete/materials/', CourseDeleteMaterialsView.as_view(),
        name='course-delete-materials'),

    # Discussion
    url(r'^discussion/', include('mediathread.discussions.urls')),

    # External Collections
    url(r'^explore/redirect/(?P<collection_id>\d+)/$',
        RedirectToExternalCollectionView.as_view(),
        name='collection_redirect'),

    # Uploader
    url(r'^upload/redirect/(?P<collection_id>\d+)/$',
        RedirectToUploaderView.as_view(),
        name='uploader_redirect'),

    url(r'^impersonate/', include('impersonate.urls')),

    url(r'^jsi18n', django.views.i18n.javascript_catalog),

    url(r'^media/(?P<path>.*)$', django.views.static.serve,
        {'document_root':
         os.path.abspath(
             os.path.join(os.path.dirname(admin.__file__), 'media')),
         'show_indexes': True}),

    # Composition Space
    url(r'^project/', include('mediathread.projects.urls')),

    # Instructor Dashboard
    url(r'^dashboard/settings/$',
        InstructorDashboardSettingsView.as_view(),
        name='course-settings-general'),

    # Reporting
    url(r'^reports/', include('mediathread.reports.urls')),

    # Bookmarklet, Wardenclyffe, Staff custom asset entry
    url(r'^save/$', AssetCreateView.as_view(), name='asset-save'),
    url(r'^update/$', AssetUpdateView.as_view(), name='asset-update-view'),

    url(r'^setting/(?P<user_name>\w[^/]*)/$', set_user_setting),

    url(r'^stats/', TemplateView.as_view(template_name='stats.html')),
    url(r'^smoketest/', include('smoketest.urls')),

    url(r'^taxonomy/', include('mediathread.taxonomy.urls')),

    url(r'^lti/', include('lti_auth.urls')),

    url(r'^test/clear/', ClearTestCache.as_view()),

    # Public To World Access ###
    url(r'^s/(?P<context_slug>\w+)/(?P<obj_type>\w+)/(?P<obj_id>\d+)/',
        ProjectPublicView.as_view(), name='collaboration-obj-view'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
