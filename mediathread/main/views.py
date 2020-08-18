from datetime import datetime
import hashlib
import hmac
import json
import re
from smtplib import SMTPRecipientsRefused, SMTPDataError

from courseaffils.columbia import CanvasTemplate, WindTemplate
from courseaffils.lib import in_course_or_404, in_course, get_public_name
from courseaffils.middleware import SESSION_KEY
from courseaffils.models import Affil, Course
from courseaffils.views import CourseListView
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.urls import reverse
from django.core.validators import validate_email
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.template import loader
from django.utils.decorators import method_decorator
from django.utils.encoding import smart_bytes, smart_text
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import DetailView
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from djangohelpers.lib import rendered_with, allow_http
import requests
from sentry_sdk import capture_exception
from threadedcomments.models import ThreadedComment

from lti_auth.models import LTICourseContext
from mediathread.api import UserResource, CourseInfoResource
from mediathread.assetmgr.api import AssetResource
from mediathread.assetmgr.models import Asset, SuggestedExternalCollection, \
    ExternalCollection
from mediathread.discussions.utils import get_course_discussions
from mediathread.djangosherd.models import SherdNote
from mediathread.main import course_details
from mediathread.main.course_details import (
    cached_course_is_faculty, course_information_title,
    has_student_activity, allow_roster_changes)
from mediathread.main.forms import (
    ContactUsForm, CourseDeleteMaterialsForm, AcceptInvitationForm,
    CourseActivateForm, DashboardSettingsForm
)
from mediathread.main.models import (
    UserSetting, CourseInvitation, PanoptoIngestLogEntry)
from mediathread.main.tasks import PanoptoIngester
from mediathread.main.util import (
    send_template_email, user_display_name, send_course_invitation_email,
    make_pmt_item
)
from mediathread.mixins import (
    ajax_required,
    AjaxRequiredMixin, JSONResponseMixin,
    LoggedInMixin, LoggedInFacultyMixin,
    LoggedInSuperuserMixin
)
from mediathread.projects.api import ProjectResource
from mediathread.projects.models import Project
from structuredcollaboration.models import Collaboration


# returns important setting information for all web pages.
def django_settings(request):
    whitelist = [
        'CAS_BASE',
        'FLOWPLAYER_SWF_LOCATION',
        'FLOWPLAYER_HTML5_SWF_LOCATION',
        'FLOWPLAYER_AUDIO_PLUGIN',
        'FLOWPLAYER_PSEUDOSTREAMING_PLUGIN',
        'FLOWPLAYER_RTMP_PLUGIN',
        'GOOGLE_ANALYTICS_ID',
        'JIRA_CONFIGURATION',
        'REVISION'
    ]

    return {'settings': dict([(k, getattr(settings, k, None))
                              for k in whitelist]),
            'EXPERIMENTAL': 'experimental' in request.COOKIES}


class SplashView(TemplateView):
    template_name = 'main/splash.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return super(SplashView, self).dispatch(request, *args, **kwargs)

        qs = Course.objects.filter(group__user=request.user)
        if qs.count() == 1:
            course_url = reverse('course_detail', args=[qs.first().id])
            return HttpResponseRedirect(course_url)
        else:
            return HttpResponseRedirect(reverse('course_list'))


@rendered_with('main/deprecated_homepage.html')
def deprecated_course_detail_view(request, course_pk):
    try:
        course = get_object_or_404(Course, pk=course_pk)
        request.course = course
        request.session[SESSION_KEY] = course
    except Course.DoesNotExist:
        return HttpResponseRedirect('/accounts/login/')

    logged_in_user = request.user
    classwork_owner = request.user  # Viewing your own work by default
    if 'username' in request.GET:
        user_name = request.GET['username']
        in_course_or_404(user_name, request.course)
        classwork_owner = get_object_or_404(User, username=user_name)

    qs = ExternalCollection.objects.filter(course=request.course)
    collections = qs.filter(uploader=False).order_by('title')
    uploader = qs.filter(uploader=True).first()

    owners = []
    if (request.course.is_member(logged_in_user) and
        (logged_in_user.is_staff or
         logged_in_user.has_perm('assetmgr.can_upload_for'))):
        owners = UserResource().render_list(request, request.course.members)

    context = {
        'classwork_owner': classwork_owner,
        'information_title': course_information_title(course),
        'faculty_feed': Project.objects.faculty_compositions(course,
                                                             logged_in_user),
        'is_faculty': cached_course_is_faculty(course, logged_in_user),
        'discussions': get_course_discussions(course),
        'msg': request.GET.get('msg', ''),
        'view': request.GET.get('view', ''),
        'collections': collections,
        'uploader': uploader,
        'can_upload': course_details.can_upload(request.user, request.course),
        'owners': owners
    }

    return context


class CourseDetailView(LoggedInMixin, DetailView):
    model = Course

    def dispatch(self, request, *args, **kwargs):
        course_pk = kwargs.get('pk')
        course = get_object_or_404(Course, pk=course_pk)
        request.course = course
        self.course = course

        # Set the course in the session cookie. This is legacy
        # functionality, but still used by the Mediathread collection
        # browser extension.
        request.session[SESSION_KEY] = course

        return super(CourseDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CourseDetailView, self).get_context_data(**kwargs)
        course = context.get('object')

        qs = ExternalCollection.objects.filter(course=self.request.course)
        collections = qs.filter(uploader=False).order_by('title')
        uploader = qs.filter(uploader=True).first()

        owners = []
        if (self.request.course.is_member(self.request.user) and
            (self.request.user.is_staff or
             self.request.user.has_perm('assetmgr.can_upload_for'))):
            owners = UserResource().render_list(self.request, course.members)

        context.update({
            'course': course,
            'classwork_owner': self.request.user,
            'information_title': course_information_title(course),
            'faculty_feed': Project.objects.faculty_compositions(
                course, self.request.user),
            'is_faculty': cached_course_is_faculty(course, self.request.user),
            'owners': owners,
            'collections': collections,
            'uploader': uploader,
            'can_upload': course_details.can_upload(self.request.user,
                                                    self.request.course),
        })
        return context


class CourseManageSourcesView(LoggedInFacultyMixin, TemplateView):
    template_name = 'dashboard/class_manage_sources.html'

    def get_context_data(self, **kwargs):
        course = self.request.course

        ingester = course_details.get_ingest_folder(course) != ''
        uploader = course_details.get_uploader(course)
        suggested = SuggestedExternalCollection.objects.all()
        upload_permission = int(course.get_detail(
            course_details.UPLOAD_PERMISSION_KEY,
            course_details.UPLOAD_PERMISSION_DEFAULT))

        return {
            'course': course,
            'suggested_collections': suggested,
            'space_viewer': self.request.user,
            'is_staff': self.request.user.is_staff,
            'uploader': uploader,
            'ingester': ingester,
            'permission_levels': course_details.UPLOAD_PERMISSION_LEVELS,
            course_details.UPLOAD_PERMISSION_KEY: upload_permission
        }

    def post(self, request, *args, **kwargs):
        kwargs.pop('course_pk')
        perm = request.POST.get(course_details.UPLOAD_PERMISSION_KEY)
        request.course.add_detail(course_details.UPLOAD_PERMISSION_KEY, perm)

        messages.add_message(request, messages.INFO,
                             'Your changes were saved.')

        return HttpResponseRedirect(
            reverse('course-manage-sources', args=[request.course.pk]))


@allow_http("POST")
@ajax_required
def set_user_setting(request, user_name):
    user = get_object_or_404(User, username=user_name)
    name = request.POST.get("name", None)
    value = request.POST.get("value", None)

    if name is None:
        return Http404("Key value not specified")

    UserSetting.set_setting(user, name, value)

    json_stream = json.dumps({'success': True})
    return HttpResponse(json_stream, content_type='application/json')


class CoursePanoptoIngestLogView(LoggedInFacultyMixin, ListView):
    model = PanoptoIngestLogEntry
    template_name = 'dashboard/class_panopto_ingest_log.html'
    paginate_by = 15

    def get_queryset(self):
        return PanoptoIngestLogEntry.objects.filter(course=self.request.course)

    def get_context_data(self, **kwargs):
        cx = super(CoursePanoptoIngestLogView, self).get_context_data(**kwargs)
        cx['base_url'] = u'{}?page='.format(
            reverse('course-panopto-ingest-log'))

        return cx


class MigrateCourseView(LoggedInFacultyMixin, TemplateView):

    template_name = 'dashboard/class_migrate.html'

    def get_context_data(self, **kwargs):
        # Only show courses for which the user is an instructor
        if self.request.user.is_superuser:
            courses = Course.objects.all()
        else:
            courses = Course.objects.filter(
                faculty_group__user=self.request.user)

        courses = courses.order_by('title').select_related('info')

        faculty = self.request.course.faculty.all().order_by(
            'last_name', 'username')

        return {
            "available_courses": courses,
            'current_course_faculty': faculty
        }

    def post(self, request, course_pk):
        from_course_id = request.POST.get('fromCourse', None)
        from_course = get_object_or_404(Course, id=from_course_id)
        faculty = [user.id for user in from_course.faculty.all()]

        include_tags = request.POST.get('include_tags', 'false') == 'true'
        include_notes = request.POST.get('include_notes', 'false') == 'true'

        # maps old ids to new objects
        object_map = {'assets': {},
                      'notes': {},
                      'projects': {}}

        owner = request.user
        if 'on_behalf_of' in request.POST:
            owner = User.objects.get(id=request.POST.get('on_behalf_of'))

        if (not in_course(owner.username, request.course) or
                not cached_course_is_faculty(request.course, owner)):
            json_stream = json.dumps({
                'success': False,
                'message': '%s is not a course member or faculty member'})
            return HttpResponse(json_stream, content_type='application/json')

        if 'asset_ids[]' in request.POST:
            asset_ids = request.POST.getlist('asset_ids[]')
            assets = Asset.objects.filter(id__in=asset_ids)
            object_map = Asset.objects.migrate(
                assets, request.course, owner, faculty, object_map,
                include_tags, include_notes)

        if 'project_ids[]' in request.POST:
            project_ids = request.POST.getlist('project_ids[]')
            projects = Project.objects.filter(id__in=project_ids)
            object_map = Project.objects.migrate(
                projects, request.course, owner, object_map,
                include_tags, include_notes)

        json_stream = json.dumps({
            'success': True,
            'asset_count': len(object_map['assets']),
            'project_count': len(object_map['projects']),
            'note_count': len(object_map['notes'])})

        return HttpResponse(json_stream, content_type='application/json')


class MigrateMaterialsView(LoggedInFacultyMixin, AjaxRequiredMixin,
                           JSONResponseMixin, View):
    """
    An ajax-only request to retrieve course information & materials
    from the perspective of the course faculty members.

    Returns:
    * Projects authored by faculty
    * Assets collected or annotated by faculty
    Example:
        /api/course/
    """

    def get(self, request, *args, **kwargs):
        course = get_object_or_404(Course, id=kwargs.pop('course_id', None))
        faculty = [user.id for user in course.faculty.all()]
        faculty_ctx = UserResource().render_list(request, course.faculty.all())

        # filter assets & notes by the faculty set
        assets = Asset.objects.by_course(course)
        if settings.SURELINK_URL:
            assets = assets.exclude(
                source__url__startswith=settings.SURELINK_URL)
        assets = assets.filter(
            sherdnote_set__author__id__in=faculty
        ).exclude(source__label='flv_pseudo')

        notes = SherdNote.objects.get_related_notes(
            assets, None, faculty, True).exclude_primary_types(['flv_pseudo'])

        ares = AssetResource(include_annotations=False)
        asset_ctx = ares.render_list(request, None, None, assets, notes)

        projects = Project.objects.by_course_and_users(course, faculty)

        # filter private projects
        if projects.count() > 0:
            collabs = Collaboration.objects.get_for_object_list(projects)
            collabs = collabs.exclude(
                policy_record__policy_name='PrivateEditorsAreOwners')
            ids = collabs.values_list('object_pk', flat=True)
            projects = projects.filter(id__in=ids)

        info_ctx = CourseInfoResource().render_one(request, course)

        ctx = {
            'course': {'id': course.id,
                       'title': course.title,
                       'faculty': faculty_ctx,
                       'info': info_ctx},
            'assets': asset_ctx,
            'projects': ProjectResource().render_list(request, projects)
        }

        return self.render_to_json_response(ctx)


class ContactUsView(FormView):
    template_name = 'main/contact.html'
    form_class = ContactUsForm
    success_url = "/contact/success/"

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super(ContactUsView, self).get_initial()
        if not self.request.user.is_anonymous:
            initial['name'] = self.request.user.get_full_name()
            initial['email'] = self.request.user.email
            initial['username'] = self.request.user.username

        initial['issue_date'] = datetime.now()

        if SESSION_KEY in self.request.session:
            initial['course'] = self.request.session[SESSION_KEY].title

        return initial

    def form_valid(self, form):
        subject = "Mediathread Contact Us Request"
        form_data = form.cleaned_data
        tmpl = loader.get_template('main/contact_description.txt')
        form_data['description'] = smart_text(tmpl.render(form_data))

        # POST to the task assignment destination
        task_url = getattr(settings, 'TASK_ASSIGNMENT_DESTINATION', None)
        if task_url is not None:
            response = requests.post(task_url, data=form_data)
            if not response.status_code == 200:
                # send to server email instead
                send_mail(subject, form_data['description'],
                          settings.SERVER_EMAIL, (settings.SERVER_EMAIL,))

        # POST to the support email
        support_email = getattr(settings, 'SUPPORT_DESTINATION', None)
        if support_email is None:
            send_template_email(
                subject, 'main/contact_email_response.txt',
                form_data, form_data['email'])
        else:
            recipients = (support_email,)
            send_mail(subject, form_data['description'],
                      settings.SERVER_EMAIL, recipients)

        return super(ContactUsView, self).form_valid(form)


class IsLoggedInView(View):

    def get(self, request, *args, **kwargs):
        """This could be a privacy hole, but since it's just logged in status,
         it seems pretty harmless"""
        logged_in = request.user.is_authenticated
        course_selected = SESSION_KEY in request.session
        current = (request.GET.get('version', None) ==
                   settings.BOOKMARKLET_VERSION)
        data = {
            "logged_in": logged_in,
            "current": current,
            "course_selected": course_selected,  # just truth value
            "ready": (logged_in and course_selected and current),
        }

        # deliver the api keys here
        if logged_in and course_selected:
            data['youtube_apikey'] = settings.YOUTUBE_BROWSER_APIKEY
            data['flickr_apikey'] = settings.DJANGOSHERD_FLICKR_APIKEY

        jscript = """(function() {
                       var status = %s;
                       if (window.SherdBookmarklet) {
                           window.SherdBookmarklet.update_user_status(status);
                       }
                       if (!window.SherdBookmarkletOptions) {
                              window.SherdBookmarkletOptions={};
                       }
                       window.SherdBookmarkletOptions.user_status = status;
                      })();
                  """ % json.dumps(data)
        return HttpResponse(jscript, content_type='application/javascript')


class IsLoggedInDataView(View):
    """
    This is similar to the IsLoggedInView, but instead of returning
    some JavaScript code along with the data, it just returns the data.
    """
    def get(self, request, *args, **kwargs):
        logged_in = request.user.is_authenticated
        course_selected = SESSION_KEY in request.session

        course_name = ''
        if SESSION_KEY in request.session:
            course_name = request.session[SESSION_KEY].title

        d = {
            'logged_in': logged_in,
            'course_selected': course_selected,
            'course_name': course_name,
        }

        if logged_in and course_selected:
            d['youtube_apikey'] = settings.YOUTUBE_BROWSER_APIKEY
            d['flickr_apikey'] = settings.DJANGOSHERD_FLICKR_APIKEY

        return HttpResponse(json.dumps(d), content_type='application/json')


class CourseDeleteMaterialsView(LoggedInSuperuserMixin, FormView):
    template_name = 'dashboard/class_delete_materials.html'
    form_class = CourseDeleteMaterialsForm

    def get_success_url(self):
        return self.success_url

    def get_context_data(self, **kwargs):
        ctx = FormView.get_context_data(self, **kwargs)
        ctx['assets'] = Asset.objects.filter(course=self.request.course)
        return ctx

    def get_delete_endpoint(self):
        url = getattr(settings, 'ASSET_DELETE_API', {})
        special = getattr(settings, 'SERVER_ADMIN_SECRETKEYS', {})
        if url and url in special.keys():
            return (url, special[url])

        return (None, None)

    def delete_uploaded_media(self, url, secret, asset):
        redirect_to = asset.get_metadata('wardenclyffe-id')[0]
        nonce = '%smthc' % datetime.now().isoformat()
        digest = hmac.new(
            smart_bytes(secret),
            smart_bytes('{}:{}:{}'.format(
                self.request.user.username,
                redirect_to,
                nonce
            )),
            hashlib.sha1).hexdigest()

        response = requests.post(url, {
            'as': self.request.user.username,
            'redirect_url': redirect_to,
            'nonce': nonce,
            'hmac': digest
        })
        return response.status_code == 200

    def form_valid(self, form):
        # delete the requested materials
        notes = SherdNote.objects.filter(asset__course=self.request.course)
        assets = Asset.objects.filter(course=self.request.course)
        projects = Project.objects.filter(course=self.request.course)

        if not form.cleaned_data['clear_all']:
            # exclude assets, projects & notes authored by faculty
            faculty = self.request.course.faculty_group.user_set.all()
            assets = assets.exclude(author__in=faculty)
            projects = projects.exclude(author__in=faculty)
            notes = notes.exclude(author__in=faculty)

        # delete all the media on CUNIX first
        (url, secret) = self.get_delete_endpoint()
        if url:
            for a in assets:
                if a.upload_references() == 1:
                    self.delete_uploaded_media(url, secret, a)

        notes.delete()
        assets.delete()
        projects.delete()

        # Clear all discussions. The root comment will be preserved.
        discussions = get_course_discussions(self.request.course)
        parents = [d.id for d in discussions]
        comments = ThreadedComment.objects.filter(parent_id__in=parents)
        comments.delete()

        # @todo - kill all unreferenced tags

        if 'delete-course' in form.data:
            messages.add_message(
                self.request, messages.INFO,
                u'{} and requested materials were deleted'.format(
                    self.request.course.title))
            self.request.course.delete()
            self.success_url = '/?unset_course'
        else:
            self.success_url = reverse(
                'course-delete-materials', args=[self.request.course.pk])
            messages.add_message(self.request, messages.INFO,
                                 'All requested materials were deleted')

        return super(CourseDeleteMaterialsView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(CourseDeleteMaterialsView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class CourseConvertMaterialsView(LoggedInSuperuserMixin, TemplateView):
    template_name = 'dashboard/class_convert_materials.html'

    def get_context_data(self, **kwargs):
        ctx = TemplateView.get_context_data(self, **kwargs)
        endpoint = getattr(settings, 'ASSET_CONVERT_API', None)
        ctx['endpoint'] = endpoint is not None
        ctx['assets'] = Asset.objects.filter(course=self.request.course)
        return ctx

    def get_conversion_endpoint(self):
        url = getattr(settings, 'ASSET_CONVERT_API', None)
        special = getattr(settings, 'SERVER_ADMIN_SECRETKEYS', {})
        if url and url in special.keys():
            return (url, special[url])

        return (None, None)

    def convert_media(self, user, course, url, secret, asset, folder):
        redirect_to = asset.get_metadata('wardenclyffe-id')[0]
        nonce = '%smthc' % datetime.now().isoformat()
        digest = hmac.new(
            smart_bytes(secret),
            smart_bytes('{}:{}:{}'.format(
                asset.author.username, redirect_to, nonce)),
            hashlib.sha1).hexdigest()

        response = requests.post(url, {
            'as': asset.author.username,
            'redirect_url': redirect_to,
            'nonce': nonce,
            'hmac': digest,
            'folder': folder,
            'audio': asset.primary.is_audio(),
            'set_course': course.group.name
        })
        return response.status_code == 200

    def convert_course_media(self, user, course, url, secret, folder):
        for a in Asset.objects.filter(course=course):
            if a.upload_references() >= 1 and not a.primary.is_panopto():
                self.convert_media(user, course, url, secret, a, folder)

    def get_upload_folder(self, course):
        folder = course_details.get_upload_folder(course)
        if not folder:
            folder = course_details.add_upload_folder(course)
        return folder

    def post(self, request, *args, **kwargs):
        success_url = reverse(
            'course-convert-materials', args=[request.course.pk])
        (url, secret) = self.get_conversion_endpoint()
        if not url:
            messages.add_message(
                self.request, messages.ERROR,
                u'Conversion endpoint is not configured')
            return HttpResponseRedirect(success_url)

        folder = self.get_upload_folder(self.request.course)

        self.convert_course_media(
            self.request.user, self.request.course, url, secret, folder)

        messages.add_message(self.request, messages.INFO,
                             'Materials were queued for conversion')
        return HttpResponseRedirect(success_url)


class CourseRosterView(LoggedInFacultyMixin, ListView):
    model = User
    template_name = 'dashboard/class_roster.html'

    def get_queryset(self):
        return self.request.course.members

    def get_context_data(self, **kwargs):
        ctx = ListView.get_context_data(self, **kwargs)
        ctx['course'] = self.request.course
        ctx['invitations'] = CourseInvitation.objects.filter(
            course=self.request.course)
        ctx['blocked'] = settings.BLOCKED_EMAIL_DOMAINS
        ctx['can_edit'] = allow_roster_changes(self.request.course)
        return ctx


class CoursePromoteUserView(LoggedInFacultyMixin, View):

    def post(self, request):
        student_id = request.POST.get('student_id', None)
        student = get_object_or_404(User, id=student_id)
        request.course.faculty_group.user_set.add(student)

        msg = u'{} is now faculty'.format(user_display_name(student))
        messages.add_message(request, messages.INFO, msg)

        return HttpResponseRedirect(
            reverse('course-roster', args=[request.course.pk]))


class CourseDemoteUserView(LoggedInFacultyMixin, View):

    def post(self, request):
        faculty_id = request.POST.get('faculty_id', None)
        faculty = get_object_or_404(User, id=faculty_id)
        request.course.faculty_group.user_set.remove(faculty)

        msg = u'{} is now a student'.format(user_display_name(faculty))
        messages.add_message(request, messages.INFO, msg)

        return HttpResponseRedirect(
            reverse('course-roster', args=[request.course.pk]))


class CourseRemoveUserView(LoggedInFacultyMixin, View):

    def post(self, request):
        user_id = request.POST.get('user_id', None)
        user = get_object_or_404(User, id=user_id)

        # @todo - leave student / faculty work?
        # Removing it could have unintended side-effects

        request.course.group.user_set.remove(user)
        request.course.faculty_group.user_set.remove(user)

        msg = u'{} is no longer a course member'.format(
            user_display_name(user))
        messages.add_message(request, messages.INFO, msg)

        return HttpResponseRedirect(
            reverse('course-roster', args=[request.course.pk]))


def unis_list(unis):
    # sometimes people enter line breaks instead of commas. allow it by
    # normalizing everything to commas
    unis = re.sub(r'\s+', ',', unis)
    return [u.strip() for u in unis.split(",") if len(u.strip()) > 0]


class CourseAddUserByUNIView(LoggedInFacultyMixin, View):

    email_template = 'dashboard/email_add_uni_user.txt'

    def validate_uni(self, uni):
        pattern = re.compile(r'^[a-z]{1,3}\d+$')
        return pattern.match(uni) is not None

    def get_or_create_user(self, uni):
        try:
            user = User.objects.get(username=uni)
        except User.DoesNotExist:
            user = User(username=uni)
            user.set_unusable_password()
            user.save()
        return user

    def post(self, request):
        unis = request.POST.get('unis', None)
        url = reverse('course-roster', args=[request.course.pk])

        if unis is None:
            msg = 'Please enter a comma-separated list of UNIs'
            messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(url)

        subj = u"Mediathread: {}".format(self.request.course.title)
        ctx = {
            'course': self.request.course,
            'domain': get_current_site(self.request).domain
        }

        for uni in unis_list(unis):
            uni = uni.lower().strip()
            if not self.validate_uni(uni):
                msg = (u'{} is not a valid UNI. To add a student without '
                       u'a UNI, click the "Invite Non-Columbia Affiliate" '
                       u'button below')
                msg = msg.format(uni)
                messages.add_message(request, messages.ERROR, msg)
                continue

            user = self.get_or_create_user(uni)
            display_name = user_display_name(user)
            if self.request.course.is_true_member(user):
                msg = u'{} ({}) is already a course member'.format(
                    display_name, uni)
                messages.add_message(request, messages.WARNING, msg)
            else:
                email = u'{}@columbia.edu'.format(uni)
                self.request.course.group.user_set.add(user)
                send_template_email(subj, self.email_template, ctx, email)
                msg = (
                    u'{} is now a course member. An email was sent to '
                    u'{} notifying the user.').format(display_name, email)

                messages.add_message(request, messages.INFO, msg)

        return HttpResponseRedirect(
            reverse('course-roster', args=[request.course.pk]))


class CourseInviteUserByEmailView(LoggedInFacultyMixin, View):

    def add_existing_user(self, user):
        add_template = 'dashboard/email_add_user.txt'
        display_name = user_display_name(user)
        if self.request.course.is_true_member(user):
            msg = u'{} ({}) is already a course member'.format(
                display_name, user.email)
            messages.add_message(self.request, messages.INFO, msg)
            return

        # add existing user to course and notify them via email
        self.request.course.group.user_set.add(user)
        subject = u"Mediathread: {}".format(self.request.course.title)
        ctx = {
            'course': self.request.course,
            'domain': get_current_site(self.request).domain,
            'user': user
        }
        send_template_email(subject, add_template, ctx, user.email)

        msg = (u'{} is now a course member. An email was sent to {} '
               u'notifying the user.').format(display_name, user.email)
        messages.add_message(self.request, messages.INFO, msg)

    def get_or_create_invite(self, email):
        try:
            invite = CourseInvitation.objects.get(
                email=email, course=self.request.course)
        except CourseInvitation.DoesNotExist:
            invite = CourseInvitation(email=email, course=self.request.course)

        invite.invited_by = self.request.user
        invite.save()
        return invite

    def invite_new_user(self, email):
        invite = self.get_or_create_invite(email)
        send_course_invitation_email(self.request, invite)

        msg = u'An email was sent to {} inviting this user to join the course.'
        msg = msg.format(email)
        messages.add_message(self.request, messages.INFO, msg)

    def validate_invite(self, email):
        try:
            validate_email(email)
        except ValidationError:
            msg = u"{} is not a valid email address.".format(email)
            raise ValidationError(msg, code='invalid')

        for suffix in settings.BLOCKED_EMAIL_DOMAINS:
            if email.endswith(suffix):
                msg = (u'{} is a Columbia University email address. To invite'
                       u' a student or instructor with a UNI, click the '
                       u'"Add Columbia Affiliate" button below')

                msg = msg.format(email)
                raise ValidationError(msg, code='blocked')

    def post(self, request):
        url = reverse('course-roster', args=[request.course.pk])
        emails = self.request.POST.get('emails', None)

        if emails is None:
            msg = 'Please enter a comma-separated list of email addresses.'
            messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(url)

        for email in emails.split(','):
            try:
                email = email.strip()
                self.validate_invite(email)

                user = User.objects.filter(email=email).first()
                if user:
                    self.add_existing_user(user)
                else:
                    self.invite_new_user(email)

            except ValidationError as e:
                messages.add_message(request, messages.ERROR, e.message)

        return HttpResponseRedirect(url)


class CourseResendInviteView(LoggedInFacultyMixin, View):

    def post(self, request):
        url = reverse('course-roster', args=[request.course.pk])
        pk = request.POST.get('invite-id', None)
        invite = get_object_or_404(CourseInvitation, pk=pk)

        send_course_invitation_email(request, invite)
        msg = u"A course invitation was resent to {}.".format(invite.email)
        messages.add_message(self.request, messages.INFO, msg)

        return HttpResponseRedirect(url)


class CourseAcceptInvitationView(FormView):
    template_name = 'registration/invitation_accept.html'
    form_class = AcceptInvitationForm

    def get_invite(self, uuid):
        try:
            return CourseInvitation.objects.filter(uuid=uuid).first()
        except (ValueError, ValidationError):
            return None  # likely a badly formed UUID string

    def get(self, request, *args, **kwargs):
        invite = self.get_invite(self.kwargs.get('uidb64', None))

        if not invite:
            raise Http404()

        form = self.get_form()
        ctx = self.get_context_data(form=form, invite=invite)
        return self.render_to_response(ctx)

    def form_valid(self, form):
        invite = self.get_invite(self.kwargs.get('uidb64', None))
        username = form.cleaned_data.get('username')
        first_name = form.cleaned_data.get('first_name')
        last_name = form.cleaned_data.get('last_name')

        user = User.objects.create(username=username, first_name=first_name,
                                   last_name=last_name, email=invite.email)
        user.set_password(form.cleaned_data.get('password1'))
        user.save()

        invite.course.group.user_set.add(user)
        invite.accepted_at = datetime.now()
        invite.accepted_user = user
        invite.save()

        return super(CourseAcceptInvitationView, self).form_valid(form)

    def get_success_url(self):
        return reverse('course-invite-complete')


class CoursePanoptoSourceView(LoggedInFacultyMixin, TemplateView):
    template_name = 'dashboard/class_panopto_source.html'

    def post(self, request, *args, **kwargs):
        ingester = PanoptoIngester(self.request)

        folder_id = self.request.POST.get('folder_name', '')
        ingester.ingest_sessions(request.course, folder_id)

        return HttpResponseRedirect(
            reverse('course-panopto-source', args=[request.course.pk]))


class InstructorDashboardSettingsView(
        LoggedInFacultyMixin, SuccessMessageMixin, UpdateView):
    model = Course
    template_name_suffix = '_update_form'
    form_class = DashboardSettingsForm
    success_message = 'The course was updated successfully.'

    def get_object(self):
        course = self.request.course
        course.refresh_from_db()
        return course

    def get_success_url(self):
        return reverse(
            'course-settings-general', args=[self.request.course.pk])

    def get_context_data(self, *args, **kwargs):
        ctx = super(InstructorDashboardSettingsView, self).get_context_data(
            *args, **kwargs)
        course = ctx.get('object')
        ctx['has_student_activity'] = has_student_activity(course)
        return ctx


class MethCourseListView(LoggedInMixin, CourseListView):
    def get_context_data(self, **kwargs):
        context = super(MethCourseListView, self).get_context_data(**kwargs)

        courses = context['object_list'].prefetch_related(
            'faculty_group__user_set')
        context.update({'courses': courses})

        courses = list(context.get('courses'))
        semester_view = self.request.GET.get('semester_view', 'current')

        affils = Affil.objects.filter(user=self.request.user, activated=False)

        # Exclude any affils that already have a course associated with
        # them, but for whatever reason have "activated" set to False.
        filtered_affils = []
        for affil in affils:
            if not affil.get_course():
                filtered_affils.append(affil)

        for affil in filtered_affils:
            affil_semester = affil.past_present_future
            if (affil_semester == -1 and semester_view == 'past') or \
               (affil_semester == 0 and semester_view == 'current') or \
               (affil_semester == 1 and semester_view == 'future'):
                courses.insert(0, affil)

        new_course = self.request.GET.get('new_course', None)
        try:
            new_course = int(new_course)
        except (TypeError, ValueError):
            pass

        context.update({
            'activatable_affils': filtered_affils,
            'courses': courses,
            'new_course': new_course,
        })
        return context


class AffilActivateView(LoggedInMixin, FormView):
    """View for activating an affiliation into a Meth Course."""
    template_name = 'main/course_activate.html'
    form_class = CourseActivateForm

    def get_success_url(self):
        past_present_future = self.affil.past_present_future
        semester_view = 'current'
        if past_present_future == 1:
            semester_view = 'future'
        elif past_present_future == 0:
            semester_view = 'current'
        elif past_present_future == -1:
            semester_view = 'past'

        new_course = self.course.pk

        return u'/?semester_view={}&new_course={}'.format(
            semester_view, new_course)

    @staticmethod
    def send_faculty_email(form, faculty_user):
        data = form.cleaned_data
        subject = u'Your Mediathread Course Activation: {}'.format(
            data.get('course_name'))
        body = u"""
Dear {},

Thank you for creating your Mediathread course: {}. You can always access this
course by going to https://mediathread.ctl.columbia.edu.

You are now ready to get started. Documentation is online here:
http://support.ctl.columbia.edu/knowledgebase/topics/6593-mediathread

If you are new to Mediathread, a CTL learning designer or your
department specialist will check in with you in the coming days to
make sure all is going well. If you have any pressing questions in the
meantime, please feel free to contact us at
ccnmtl-mediathread@ccnmtl.columbia.edu.

Thanks,
The Mediathread Team
""".format(user_display_name(faculty_user),
           data.get('course_name'))
        send_mail(
            subject,
            body,
            settings.SERVER_EMAIL,
            [faculty_user.email])

    @staticmethod
    def send_staff_email(form, faculty_user):
        data = form.cleaned_data
        subject = u'Mediathread Course Activated: {}'.format(
            data.get('course_name'))
        body = u"""
Course Title: {}

Date Range: {} - {}

Consult/Demo request: {}

How will Mediathread be used to improve your class?
{}

How did you hear about Mediathread? {}

Have you used Mediathread before? {}

Faculty: {} <{}>
""".format(data.get('course_name'),
           data.get('date_range_start'),
           data.get('date_range_end'),
           data.get('request_consult_or_demo'),
           data.get('how_will_mediathread_improve_your_class'),
           data.get('hear_about_mediathread'),
           data.get('used_mediathread'),
           user_display_name(faculty_user),
           faculty_user.email)

        send_mail(
            subject,
            body,
            settings.SERVER_EMAIL,
            [settings.SERVER_EMAIL])

    def create_course(self, form, affil):
        """Creates a Course for this form.

        Returns (course, created) as a tuple.
        """
        # Create the course.
        studentaffil = re.sub(r'\.fc\.', '.st.', affil.name)
        g = Group.objects.get_or_create(name=studentaffil)[0]
        fg = Group.objects.get_or_create(name=affil.name)[0]

        c, created = Course.objects.get_or_create(
            group=g,
            faculty_group=fg,
            defaults={'title': form.cleaned_data.get('course_name')})

        return c, created

    def init_created_course(self, course, affil):
        # Add the current user as an instructor.
        course.group.user_set.add(self.request.user)
        course.faculty_group.user_set.add(self.request.user)
        course.add_detail('instructor',
                          get_public_name(self.request.user, self.request))

        # Get the year and term from the affil string.
        affil_dict = {}
        if hasattr(settings, 'COURSEAFFILS_COURSESTRING_MAPPER'):
            affil_dict = settings.COURSEAFFILS_COURSESTRING_MAPPER.to_dict(
                affil.name)
        if affil_dict:
            course.info.year = affil_dict.get('year')
            course.info.term = affil_dict.get('term')
            course.info.save()

    def get_context_data(self, *args, **kwargs):
        context = super(AffilActivateView, self).get_context_data(
            *args, **kwargs)
        pk = self.kwargs.get('pk')
        self.affil = Affil.objects.get(pk=pk)
        affil_dict = self.affil.to_dict()

        c = self.affil.get_course()
        if c:
            # If a Course already exists for this affil, show an error.
            msg = (u'The {} affil is already connected to the course:'
                   u' <strong><a href="/?set_course={}">{}</a>'
                   u'</strong>'.format(
                       self.affil,
                       c.group.name,
                       c))
            messages.error(self.request, mark_safe(msg))  # nosec
        context.update({
            'affil': self.affil,
            'term': affil_dict['term'],
            'year': affil_dict['year'],
        })
        return context

    @staticmethod
    def make_pmt_activation_item(form, faculty_user):
        """Make a PMT item for course activation.

        Returns the requests object, or None.
        """
        milestone_id = getattr(
            settings, 'MEDIATHREAD_PMT_MILESTONE_ID', None)
        owner_username = getattr(
            settings, 'MEDIATHREAD_PMT_OWNER_USERNAME', None)
        if milestone_id and owner_username:
            # Prepare data entry into PMT. See
            # dmt.views.api.ExternalAddItemView.
            data = form.cleaned_data

            description = ''
            for k in data:
                description += u'{}: {}\n'.format(k, data[k])

            description += u'Faculty: {} <{}>\n'.format(
                user_display_name(faculty_user),
                faculty_user.email)

            pmt_data = {
                'mid': milestone_id,
                'owner': owner_username,
                'assigned_to': owner_username,
                'type': 'action item',
                'title': 'Course Activated: {}'.format(
                    data.get('course_name')),
                'description': description,
            }
            try:
                return make_pmt_item(pmt_data)
            except ImproperlyConfigured:
                # If the PMT item creation fails, we'll have the staff email.
                pass

        return None

    def form_valid(self, form):
        pk = self.kwargs.get('pk')
        self.affil = Affil.objects.get(pk=pk)
        self.affil.activated = True
        self.affil.save()

        course, created = self.create_course(form, self.affil)

        self.course = course

        if created:
            self.init_created_course(self.course, self.affil)
        else:
            capture_exception(
                u'Attempted to create duplicate course for affil: ' +
                u'{} - {}  Course: {}'.format(
                    self.affil.pk, self.affil.name,
                    self.course.title))
            messages.error(
                self.request,
                u'There was an error activating your course. The ' +
                u'<strong><a href="?{}">{}</a></strong> '.format(
                    urlencode({'set_course': self.course.group.name}),
                    self.course.title) +
                u'course already exists.')
            return super(AffilActivateView, self).form_valid(form)

        try:
            self.send_faculty_email(form, self.request.user)
        except (SMTPDataError, SMTPRecipientsRefused) as e:
            messages.error(self.request, 'Failed to send faculty email.')
            capture_exception(str(e))

        try:
            self.send_staff_email(form, self.request.user)
        except (SMTPDataError, SMTPRecipientsRefused) as e:
            messages.error(self.request, 'Failed to send staff email.')
            capture_exception(str(e))

        messages.success(self.request, 'You\'ve activated your course.')
        self.make_pmt_activation_item(form, self.request.user)
        return super(AffilActivateView, self).form_valid(form)


class LTICourseSelector(LoggedInMixin, View):

    def get(self, request, context):
        try:
            messages.add_message(
                request, messages.INFO,
                'Reminder: please log out of Mediathread '
                'after you log out of Courseworks.')

            ctx = LTICourseContext.objects.get(lms_course_context=context)
            url = reverse('course_detail', args=[ctx.group.course.id])
        except LTICourseContext.DoesNotExist:
            url = '/'

        return HttpResponseRedirect(url)


@method_decorator(xframe_options_exempt, name='dispatch')
class LTICourseCreate(LoggedInMixin, View):

    def notify_staff(self, course):
        data = {
            'course': course,
            'domain': self.request.POST.get('domain'),
            'user': self.request.user
        }
        send_template_email(
            'Mediathread Course Connected',
            'main/notify_lti_course_connect.txt',
            data, settings.SERVER_EMAIL)

    def thank_faculty(self, course):
        send_template_email(
            'Mediathread Course Connected',
            'main/lti_course_connect.txt',
            {'course': course}, self.request.user.email)

    def groups_from_context(self, course_context):
        group, created = Group.objects.get_or_create(name=course_context)
        faculty_group, created = Group.objects.get_or_create(
            name='{}_faculty'.format(course_context))
        return (group, faculty_group)

    def groups_from_sis_course_id(self, attrs):
        st_affil = WindTemplate.to_string(attrs)
        group, created = Group.objects.get_or_create(name=st_affil)
        self.request.user.groups.add(group)

        attrs['member'] = 'fc'
        fc_affil = WindTemplate.to_string(attrs)
        faculty_group, created = Group.objects.get_or_create(name=fc_affil)
        self.request.user.groups.add(faculty_group)
        return (group, faculty_group)

    def get_year_and_term_from_sis_course_id(self, sis_course_id):
        m = re.match(
            (r'(?P<year>\d{4})(?P<term>\d{2})'), sis_course_id)
        if m:
            return m.groupdict()

    def post(self, *args, **kwargs):
        course_context = self.request.POST.get('lms_course')
        title = self.request.POST.get('lms_course_title')

        sis_course_id = self.request.POST.get('sis_course_id', '')
        d = CanvasTemplate.to_dict(sis_course_id)

        if d:
            (group, faculty_group) = self.groups_from_sis_course_id(d)
        else:
            (group, faculty_group) = self.groups_from_context(course_context)
            yt = self.get_year_and_term_from_sis_course_id(sis_course_id)

        self.request.user.groups.add(group)
        self.request.user.groups.add(faculty_group)

        course, created = Course.objects.get_or_create(
            group=group, faculty_group=faculty_group,
            defaults={'title': title})

        if d:
            # Add CourseInfo from the fields
            course.info.term = d['term']
            course.info.year = d['year']
            course.info.save()
        elif yt:
            course.info.term = yt['term']
            course.info.year = yt['year']
            course.info.save()

        # hook up the context
        (ctx, created) = LTICourseContext.objects.get_or_create(
            group=group, faculty_group=faculty_group,
            lms_course_context=course_context)

        messages.add_message(
            self.request, messages.INFO,
            u'<strong>Success!</strong> ' +
            u'{} is connected to Mediathread.'.format(title))

        self.notify_staff(course)
        self.thank_faculty(course)

        url = reverse('lti-landing-page', args=[course_context])
        return HttpResponseRedirect(url)


def error_500(request):
    raise Exception('Test exception')
