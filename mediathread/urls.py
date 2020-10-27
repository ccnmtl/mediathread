import os.path

import courseaffils
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import (
    PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView,
    PasswordResetCompleteView,
    PasswordResetConfirmView
)
from django.contrib.auth.views import LogoutView, LoginView
import django.contrib.auth.views
from django.urls import include, path
from django.views.generic.base import TemplateView
from django.views.i18n import JavaScriptCatalog
import django.views.i18n
import django.views.static
import djangowind.views
from mediathread.api import CourseResource
from mediathread.assetmgr.views import (
    AssetCollectionView,
    AssetDetailView, ReactAssetDetailView,
    TagCollectionView,
    RedirectToExternalCollectionView, RedirectToUploaderView,
    AssetCreateView, BookmarkletMigrationView, AssetUpdateView)
from mediathread.main.forms import CustomRegistrationForm
from mediathread.main.views import (
    error_500,
    MethCourseListView, AffilActivateView,
    InstructorDashboardSettingsView,
    ContactUsView, IsLoggedInView, IsLoggedInDataView,
    MigrateMaterialsView, MigrateCourseView, CourseManageSourcesView,
    CourseDeleteMaterialsView, CourseDetailView,
    deprecated_course_detail_view,
    CourseRosterView, CoursePromoteUserView, CourseDemoteUserView,
    CourseRemoveUserView, CourseAddUserByUNIView,
    CourseInviteUserByEmailView, CourseAcceptInvitationView,
    CourseResendInviteView, set_user_setting, CoursePanoptoSourceView,
    CoursePanoptoIngestLogView, CourseConvertMaterialsView,
    LTICourseSelector, LTICourseCreate, SplashView)
from mediathread.projects.views import (
    ProjectCollectionView, ProjectDetailView, ProjectItemView,
    ProjectPublicView, ProjectListView, AssignmentListView)
from mediathread.taxonomy.api import TermResource, VocabularyResource
from registration.backends.default.views import RegistrationView
from tastypie.api import Api


tastypie_api = Api('')
tastypie_api.register(TermResource())
tastypie_api.register(VocabularyResource())
tastypie_api.register(CourseResource())

admin.autodiscover()

bookmarklet_root = os.path.join(os.path.dirname(__file__),
                                '../media/',
                                'bookmarklets')

redirect_after_logout = getattr(settings, 'LOGOUT_REDIRECT_URL', None)

auth_urls = path('accounts/', include('django.contrib.auth.urls'))

logout_page = path('accounts/logout/',
                   LogoutView.as_view(),
                   {'next_page': redirect_after_logout})
admin_logout_page = path('accounts/logout/',
                         LogoutView.as_view(),
                         {'next_page': '/admin/'})

if hasattr(settings, 'CAS_BASE'):
    auth_urls = path('accounts/', include('djangowind.urls'))
    logout_page = path('accounts/logout/',
                       djangowind.views.logout,
                       {'next_page': redirect_after_logout})
    admin_logout_page = path('admin/logout/',
                             djangowind.views.logout,
                             {'next_page': redirect_after_logout})


urlpatterns = [
    path('', SplashView.as_view(), name='splash'),
    path('course/<int:course_pk>/oldhome/',
         deprecated_course_detail_view,
         name='home'),
    path('500', error_500, name='error_500'),
    admin_logout_page,
    logout_page,
    path('admin/', admin.site.urls),

    path('accounts/login/',
         LoginView.as_view(template_name='registration/login_darkmode.html'),
         name='login'),

    # override the default urls for password
    path('password/change/',
         PasswordChangeView.as_view(),
         name='password_change'),
    path('password/change/done/',
         PasswordChangeDoneView.as_view(),
         name='password_change_done'),
    path('password/reset/',
         PasswordResetView.as_view(),
         name='password_reset'),
    path('password/reset/done/',
         PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('password/reset/complete/',
         PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
    path('password/reset/confirm/<uuid:uidb64>-<str:token>/',
         PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),

    path('accounts/invite/accept/<uuid:uidb64>/',
         CourseAcceptInvitationView.as_view(),
         name='course-invite-accept'),
    path('accounts/invite/complete/', TemplateView.as_view(
        template_name='registration/invitation_complete.html'),
         name='course-invite-complete'),

    path('accounts/register/',
         RegistrationView.as_view(form_class=CustomRegistrationForm),
         name='registration_register'),
    path('accounts/', include('registration.backends.default.urls')),

    # API - JSON rendering layers. Half hand-written, half-straight tasty=pie
    path('api/asset/user/<slug:record_owner_name>/',
         AssetCollectionView.as_view(), {}, 'assets-by-user'),
    path('api/asset/<int:asset_id>/', AssetDetailView.as_view(),
         {}, 'asset-detail'),
    path('api/asset/', AssetCollectionView.as_view(), {},
         'assets-by-course'),
    path('api/user/courses', courseaffils.views.course_list_query,
         name='api-user-courses'),
    path('api/tag/', TagCollectionView.as_view(), {},
         'tag-collection-view'),
    path('api/project/user/<slug:record_owner_name>/',
         ProjectCollectionView.as_view(), {}, 'project-by-user'),
    path('api/project/<int:project_id>/<int:asset_id>/',
         ProjectItemView.as_view(), {}, 'project-item-view'),
    path('api/project/<int:project_id>/', ProjectDetailView.as_view(),
         {}, 'asset-detail'),
    path('api/project/', ProjectCollectionView.as_view(), {}),
    path('api', include(tastypie_api.urls)),

    # Collections Space
    path('asset/', include('mediathread.assetmgr.urls')),

    path('sequence/', include('mediathread.sequence.urls')),

    auth_urls,  # see above

    # Bookmarklet + cache defeating
    path('bookmarklets/<path:path>analyze.js', django.views.static.serve,
         {'document_root': bookmarklet_root}, name='analyze-bookmarklet'),
    path('nocache/\w+/bookmarklets/<path:path>',
         django.views.static.serve, {'document_root': bookmarklet_root},
         name='nocache-analyze-bookmarklet'),

    path('comments/', include('django_comments.urls')),

    # Contact us forms.
    path('contact/success/',
         TemplateView.as_view(template_name='main/contact_success.html')),
    path('contact/', ContactUsView.as_view(), name='contact-us'),
    path('course/request/success/', TemplateView.as_view(
        template_name='main/course_request_success.html')),
    path('affil/<int:pk>/activate/',
         AffilActivateView.as_view(),
         name='affil_activate'),

    # New course-aware routes
    path('course/<int:course_pk>/react/asset/<int:pk>/',
         ReactAssetDetailView.as_view(),
         name='react_asset_detail'),
    path('course/<int:course_pk>/react/asset/<int:pk>/'
         'annotations/<int:annotation_pk>/',
         ReactAssetDetailView.as_view(),
         name='react_annotation_detail'),
    path('course/<int:pk>/', CourseDetailView.as_view(),
         name='course_detail'),
    path('course/<int:course_pk>/asset/',
         include('mediathread.assetmgr.urls')),
    path('course/<int:course_pk>/project/',
         include('mediathread.projects.urls')),
    path('course/<int:course_pk>/discussion/',
         include('mediathread.discussions.urls')),

    path('course/list/',
         MethCourseListView.as_view(),
         name='course_list'),
    path('course/lti/create/',
         LTICourseCreate.as_view(), name='lti-course-create'),
    path('course/lti/<slug:context>/',
         LTICourseSelector.as_view(), name='lti-course-select'),

    path('course/<int:course_pk>/projects/',
         ProjectListView.as_view(),
         name='project-list'),
    path('course/<int:course_pk>/assignments/',
         AssignmentListView.as_view(),
         name='assignment-list'),

    # Bookmarklet
    path('accounts/logged_in.js', IsLoggedInView.as_view(), {},
         name='is_logged_in.js'),
    path('accounts/is_logged_in/', IsLoggedInDataView.as_view(), {},
         name='is_logged_in'),
    path('bookmarklet_migration/', BookmarkletMigrationView.as_view(), {},
         name='bookmarklet_migration'),

    path('crossdomain.xml', django.views.static.serve, {
        'document_root': os.path.join(os.path.dirname(__file__), '../media/'),
        'path': 'crossdomain.xml'
    }),

    path('dashboard/migrate/materials/<int:course_id>/',
         MigrateMaterialsView.as_view(), {}, 'dashboard-migrate-materials'),
    path('course/<int:course_pk>/dashboard/migrate/',
         MigrateCourseView.as_view(),
         {}, 'dashboard-migrate'),
    path('dashboard/roster/promote/', CoursePromoteUserView.as_view(),
         name='course-roster-promote'),
    path('dashboard/roster/demote/', CourseDemoteUserView.as_view(),
         name='course-roster-demote'),
    path('dashboard/roster/remove/', CourseRemoveUserView.as_view(),
         name='course-roster-remove'),
    path('dashboard/roster/add/uni/', CourseAddUserByUNIView.as_view(),
         name='course-roster-add-uni'),
    path('dashboard/roster/add/email/', CourseInviteUserByEmailView.as_view(),
         name='course-roster-invite-email'),
    path('dashboard/roster/resend/email/', CourseResendInviteView.as_view(),
         name='course-roster-resend-email'),
    path('course/<int:course_pk>/dashboard/roster/',
         CourseRosterView.as_view(),
         name='course-roster'),

    path('course/<int:course_pk>/dashboard/sources/',
         CourseManageSourcesView.as_view(),
         name='course-manage-sources'),
    path('course/<int:course_pk>/dashboard/delete/materials/',
         CourseDeleteMaterialsView.as_view(),
         name='course-delete-materials'),
    path('course/<int:course_pk>/dashboard/convert/materials/',
         CourseConvertMaterialsView.as_view(),
         name='course-convert-materials'),
    path('course/<int:course_pk>/dashboard/ingest/',
         CoursePanoptoIngestLogView.as_view(),
         name='course-panopto-ingest-log'),
    path('course/<int:course_pk>/dashboard/panopto/',
         CoursePanoptoSourceView.as_view(),
         name='course-panopto-source'),

    # Discussion
    path('discussion/', include('mediathread.discussions.urls')),

    # External Collections
    path('explore/redirect/<int:collection_id>/',
         RedirectToExternalCollectionView.as_view(),
         name='collection_redirect'),

    # Uploader
    path('upload/redirect/<int:collection_id>/',
         RedirectToUploaderView.as_view(),
         name='uploader_redirect'),

    path('impersonate/', include('impersonate.urls')),

    path('jsi18n', JavaScriptCatalog.as_view()),

    path('media/<path:path>', django.views.static.serve,
         {'document_root':
          os.path.abspath(
              os.path.join(os.path.dirname(admin.__file__), 'media')),
          'show_indexes': True}),

    # Composition Space
    path('project/', include('mediathread.projects.urls')),

    # Instructor Dashboard
    path('course/<int:course_pk>/dashboard/settings/',
         InstructorDashboardSettingsView.as_view(),
         name='course-settings-general'),

    # Reporting
    path('course/<int:course_pk>/reports/',
         include('mediathread.reports.urls')),

    # Bookmarklet, Wardenclyffe, Staff custom asset entry
    path('save/', AssetCreateView.as_view(), name='asset-save'),
    path('update/', AssetUpdateView.as_view(), name='asset-update-view'),

    path('setting/<slug:user_name>/', set_user_setting),

    path('stats/', TemplateView.as_view(template_name='stats.html')),
    path('smoketest/', include('smoketest.urls')),

    path('course/<int:course_pk>/taxonomy/',
         include('mediathread.taxonomy.urls')),

    path('lti/', include('lti_auth.urls')),

    # Public To World Access ###
    path('s/<slug:context_slug>/<slug:obj_type>/<int:obj_id>/',
         ProjectPublicView.as_view(), name='collaboration-obj-view'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
