from datetime import datetime
import json
import re

from smtplib import SMTPRecipientsRefused
from courseaffils.lib import in_course_or_404, in_course, get_public_name
from courseaffils.middleware import SESSION_KEY
from courseaffils.models import Affil, Course
from courseaffils.views import get_courses_for_user, CourseListView
from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.template import loader
from django.template.context import Context
from django.utils.safestring import mark_safe
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from djangohelpers.lib import rendered_with, allow_http
import requests
from threadedcomments.models import ThreadedComment
import waffle

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
    has_student_activity
)
from mediathread.main.forms import (
    RequestCourseForm, ContactUsForm,
    CourseDeleteMaterialsForm, AcceptInvitationForm,
    CourseActivateForm, DashboardSettingsForm
)
from mediathread.main.models import UserSetting, CourseInvitation
from mediathread.main.util import send_template_email, user_display_name, \
    send_course_invitation_email
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
    whitelist = ['FLOWPLAYER_SWF_LOCATION',
                 'FLOWPLAYER_HTML5_SWF_LOCATION',
                 'FLOWPLAYER_AUDIO_PLUGIN',
                 'FLOWPLAYER_PSEUDOSTREAMING_PLUGIN',
                 'FLOWPLAYER_RTMP_PLUGIN',
                 'DEBUG',
                 'REVISION',
                 'DATABASES',
                 'GOOGLE_ANALYTICS_ID',
                 'CAS_BASE']

    return {'settings': dict([(k, getattr(settings, k, None))
                              for k in whitelist]),
            'EXPERIMENTAL': 'experimental' in request.COOKIES}


@rendered_with('homepage.html')
def course_detail_view(request):
    if not request.course:
        return HttpResponseRedirect('/accounts/login/')

    logged_in_user = request.user
    classwork_owner = request.user  # Viewing your own work by default
    if 'username' in request.GET:
        user_name = request.GET['username']
        in_course_or_404(user_name, request.course)
        classwork_owner = get_object_or_404(User, username=user_name)

    course = request.course

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
        "information_title": course_information_title(course),
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

    if getattr(settings, 'DJANGOSHERD_FLICKR_APIKEY', None):
        # MUST only contain string values for now!!
        # (see templates/assetmgr/bookmarklet.js to see why or fix)
        context['bookmarklet_vars'] = {
            'flickr_apikey': settings.DJANGOSHERD_FLICKR_APIKEY
        }

    return context


class CourseManageSourcesView(LoggedInFacultyMixin, TemplateView):
    template_name = 'dashboard/class_manage_sources.html'

    def get_context_data(self, **kwargs):
        course = self.request.course

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
            'permission_levels': course_details.UPLOAD_PERMISSION_LEVELS,
            course_details.UPLOAD_PERMISSION_KEY: upload_permission
        }

    def post(self, request):
        perm = request.POST.get(
            course_details.UPLOAD_PERMISSION_KEY)
        request.course.add_detail(course_details.UPLOAD_PERMISSION_KEY, perm)

        messages.add_message(request, messages.INFO,
                             'Your changes were saved.')

        return HttpResponseRedirect(reverse("class-manage-sources"))


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


class MigrateCourseView(LoggedInFacultyMixin, TemplateView):

    template_name = 'dashboard/class_migrate.html'

    def get_context_data(self, **kwargs):
        # Only show courses for which the user is an instructor
        available_courses = get_courses_for_user(self.request.user)
        courses = []
        if self.request.user.is_superuser:
            courses = available_courses
        else:
            for course in available_courses:
                if cached_course_is_faculty(course, self.request.user):
                    courses.append(course)

        # Only send down the real faculty. Not all us staff members
        faculty = []
        for user in self.request.course.faculty.all().order_by('last_name',
                                                               'username'):
            faculty.append(user)

        return {
            "current_course_faculty": faculty,
            "available_courses": courses
        }

    def post(self, request):
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
        assets = assets.filter(sherdnote_set__author__id__in=faculty)
        notes = SherdNote.objects.get_related_notes(
            assets, None, faculty, True)

        ares = AssetResource(include_annotations=False)
        asset_ctx = ares.render_list(request, None, None, assets, notes)

        projects = Project.objects.by_course_and_users(course, faculty)

        # filter private projects
        if projects.count() > 0:
            collabs = Collaboration.objects.get_for_object_list(projects)
            collabs = collabs.exclude(
                policy_record__policy_name='PrivateEditorsAreOwners')
            ids = [int(c.object_pk) for c in collabs]
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


class RequestCourseView(FormView):
    template_name = 'main/course_request.html'
    form_class = RequestCourseForm
    success_url = "/course/request/success/"

    def form_valid(self, form):
        subject = "Mediathread Course Request"
        form_data = form.cleaned_data
        tmpl = loader.get_template('main/course_request_description.txt')
        form_data['description'] = tmpl.render(Context(form_data))

        task_url = getattr(settings, 'TASK_ASSIGNMENT_DESTINATION', None)
        if task_url is not None:
            response = requests.post(task_url, data=form_data)
            if not response.status_code == 200:
                # send to server email instead
                send_mail(subject, form_data['description'],
                          form_data['email'], (settings.SERVER_EMAIL,))

        return super(RequestCourseView, self).form_valid(form)


class ContactUsView(FormView):
    template_name = 'main/contact.html'
    form_class = ContactUsForm
    success_url = "/contact/success/"

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super(ContactUsView, self).get_initial()
        if not self.request.user.is_anonymous():
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
        form_data['description'] = unicode(tmpl.render(Context(form_data)))

        # POST to the task assignment destination
        task_url = getattr(settings, 'TASK_ASSIGNMENT_DESTINATION', None)
        if task_url is not None:
            response = requests.post(task_url, data=form_data)
            if not response.status_code == 200:
                # send to server email instead
                send_mail(subject, form_data['description'],
                          form_data['email'], (settings.SERVER_EMAIL,))

        # POST to the support email
        support_email = getattr(settings, 'SUPPORT_DESTINATION', None)
        if support_email is None:
            send_template_email(
                subject, 'main/contact_email_response.txt',
                form_data, form_data['email'])
        else:
            sender = form_data['email']
            recipients = (support_email,)
            send_mail(subject, form_data['description'], sender, recipients)

        return super(ContactUsView, self).form_valid(form)


class IsLoggedInView(View):

    def get(self, request, *args, **kwargs):
        """This could be a privacy hole, but since it's just logged in status,
         it seems pretty harmless"""
        logged_in = request.user.is_authenticated()
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
        logged_in = request.user.is_authenticated()
        course_selected = SESSION_KEY in request.session

        course_name = ''
        if 'ccnmtl.courseaffils.course' in request.session:
            course_name = request.session['ccnmtl.courseaffils.course'].title

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
        return reverse('course-delete-materials')

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

        notes.delete()
        assets.delete()
        projects.delete()

        # Clear all discussions. The root comment will be preserved.
        discussions = get_course_discussions(self.request.course)
        parents = [d.id for d in discussions]
        comments = ThreadedComment.objects.filter(parent_id__in=parents)
        comments.delete()

        # @todo - kill all unreferenced tags

        messages.add_message(self.request, messages.INFO,
                             'All requested materials were deleted')

        return super(CourseDeleteMaterialsView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(CourseDeleteMaterialsView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class CourseRosterView(LoggedInFacultyMixin, ListView):
    model = User
    template_name = 'dashboard/class_roster.html'

    def get_queryset(self):
        return self.request.course.members

    def get_context_data(self, **kwargs):
        ctx = ListView.get_context_data(self, **kwargs)
        ctx['invitations'] = CourseInvitation.objects.filter(
            course=self.request.course)
        ctx['blocked'] = settings.BLOCKED_EMAIL_DOMAINS
        return ctx


class CoursePromoteUserView(LoggedInFacultyMixin, View):

    def post(self, request):
        student_id = request.POST.get('student_id', None)
        student = get_object_or_404(User, id=student_id)
        request.course.faculty_group.user_set.add(student)

        msg = '{} is now faculty'.format(user_display_name(student))
        messages.add_message(request, messages.INFO, msg)

        return HttpResponseRedirect(reverse('course-roster'))


class CourseDemoteUserView(LoggedInFacultyMixin, View):

    def post(self, request):
        faculty_id = request.POST.get('faculty_id', None)
        faculty = get_object_or_404(User, id=faculty_id)
        request.course.faculty_group.user_set.remove(faculty)

        msg = '{} is now a student'.format(user_display_name(faculty))
        messages.add_message(request, messages.INFO, msg)

        return HttpResponseRedirect(reverse('course-roster'))


class CourseRemoveUserView(LoggedInFacultyMixin, View):

    def post(self, request):
        user_id = request.POST.get('user_id', None)
        user = get_object_or_404(User, id=user_id)

        # @todo - leave student / faculty work?
        # Removing it could have unintended side-effects

        request.course.group.user_set.remove(user)
        request.course.faculty_group.user_set.remove(user)

        msg = '{} is no longer a course member'.format(user_display_name(user))
        messages.add_message(request, messages.INFO, msg)

        return HttpResponseRedirect(reverse('course-roster'))


def unis_list(unis):
    return [u.strip() for u in unis.split(",") if len(u.strip()) > 0]


class CourseAddUserByUNIView(LoggedInFacultyMixin, View):

    email_template = 'dashboard/email_add_uni_user.txt'

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
        url = reverse('course-roster')

        if unis is None:
            msg = 'Please enter a comma-separated list of UNIs'
            messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(url)

        subj = "Mediathread: {}".format(self.request.course.title)
        ctx = {
            'course': self.request.course,
            'domain': get_current_site(self.request).domain
        }

        for uni in unis_list(unis):
            user = self.get_or_create_user(uni)
            display_name = user_display_name(user)
            if self.request.course.is_true_member(user):
                msg = '{} ({}) is already a course member'.format(
                    display_name, uni)
                messages.add_message(request, messages.WARNING, msg)
            else:
                email = '{}@columbia.edu'.format(uni)
                self.request.course.group.user_set.add(user)
                send_template_email(subj, self.email_template, ctx, email)
                msg = (
                    '{} is now a course member. An email was sent to '
                    '{} notifying the user.').format(display_name, email)

                messages.add_message(request, messages.INFO, msg)

        return HttpResponseRedirect(reverse('course-roster'))


class CourseInviteUserByEmailView(LoggedInFacultyMixin, View):

    def add_existing_user(self, user):
        add_template = 'dashboard/email_add_user.txt'
        display_name = user_display_name(user)
        if self.request.course.is_true_member(user):
            msg = '{} ({}) is already a course member'.format(
                display_name, user.email)
            messages.add_message(self.request, messages.INFO, msg)
            return

        # add existing user to course and notify them via email
        self.request.course.group.user_set.add(user)
        subject = "Mediathread: {}".format(self.request.course.title)
        ctx = {
            'course': self.request.course,
            'domain': get_current_site(self.request).domain
        }
        send_template_email(subject, add_template, ctx, user.email)

        msg = ('{} is now a course member. An email was sent to {} '
               'notifying the user.').format(display_name, user.email)
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

        msg = "{} was invited to join the course.".format(email)
        messages.add_message(self.request, messages.INFO, msg)

    def validate_invite(self, email):
        try:
            validate_email(email)
        except ValidationError:
            msg = "{} is not a valid email address.".format(email)
            raise ValidationError(msg, code='invalid')

        for suffix in settings.BLOCKED_EMAIL_DOMAINS:
            if email.endswith(suffix):
                msg = "{} cannot be invited through email.".format(email)
                raise ValidationError(msg, code='blocked')

    def post(self, request):
        url = reverse('course-roster')
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

            except ValidationError, e:
                messages.add_message(request, messages.ERROR, e.message)

        return HttpResponseRedirect(url)


class CourseResendInviteView(LoggedInFacultyMixin, View):

    def post(self, request):
        url = reverse('course-roster')
        pk = request.POST.get('invite-id', None)
        invite = get_object_or_404(CourseInvitation, pk=pk)

        send_course_invitation_email(request, invite)
        msg = "A course invitation was resent to {}.".format(invite.email)
        messages.add_message(self.request, messages.INFO, msg)

        return HttpResponseRedirect(url)


class CourseAcceptInvitationView(FormView):
    template_name = 'registration/invitation_accept.html'
    form_class = AcceptInvitationForm

    def get_invite(self, uuid):
        try:
            return CourseInvitation.objects.filter(uuid=uuid).first()
        except ValueError:
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


class InstructorDashboardView(LoggedInFacultyMixin, DetailView):
    model = Course
    template_name = 'main/instructor_dashboard.html'

    def get_object(self):
        return self.request.course

    def get_context_data(self, *args, **kwargs):
        ctx = super(InstructorDashboardView, self).get_context_data(
            *args, **kwargs)
        ctx.update({'course': ctx.get('object')})
        return ctx


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
        return reverse('course-settings-general')

    def get_context_data(self, *args, **kwargs):
        ctx = super(InstructorDashboardSettingsView, self).get_context_data(
            *args, **kwargs)
        course = ctx.get('object')
        lti_context = LTICourseContext.objects.filter(
            group=course.group.id,
            faculty_group=course.faculty_group.id).first()
        ctx['lti_context'] = lti_context
        ctx['has_student_activity'] = has_student_activity(course)
        return ctx


class MethCourseListView(LoggedInMixin, CourseListView):
    template_name = 'main/course_list.html'

    def get_context_data(self, **kwargs):
        context = super(MethCourseListView, self).get_context_data(**kwargs)
        context.update({'courses': context['object_list']})
        if not waffle.flag_is_active(self.request, 'course_activation'):
            return context

        courses = list(context.get('courses'))
        semester_view = self.request.GET.get('semester_view', 'current')
        affils = Affil.objects.filter(user=self.request.user, activated=False)
        for affil in affils:
            affil_semester = affil.past_present_future
            if (affil_semester == -1 and semester_view == 'past') or \
               (affil_semester == 0 and semester_view == 'current') or \
               (affil_semester == 1 and semester_view == 'future'):
                courses.insert(0, affil)

        context.update({
            'activatable_affils': affils,
            'courses': courses,
        })
        return context


class AffilActivateView(LoggedInMixin, FormView):
    """View for activating an affiliation into a Meth Course."""
    template_name = 'main/course_activate.html'
    form_class = CourseActivateForm
    success_url = '/'

    @staticmethod
    def send_faculty_email(form, faculty_user):
        data = form.cleaned_data
        subject = 'Your Mediathread Course Activation: {}'.format(
            data.get('course_name'))
        body = """
Course Name: {}
Term: {}
Year: {}
Consult or Demo: {}
""".format(data.get('course_name'),
           data.get('term'),
           data.get('year'),
           data.get('consult_or_demo'))

        send_mail(
            subject,
            body,
            settings.SERVER_EMAIL,
            [faculty_user.email])

    @staticmethod
    def send_staff_email(form, faculty_user):
        data = form.cleaned_data
        subject = 'Mediathread Course Activated: {}'.format(
            data.get('course_name'))
        body = """
Course Name: {}
Term: {}
Year: {}
Consult or Demo: {}
Faculty: {} {} <{}>
""".format(data.get('course_name'),
           data.get('term'),
           data.get('year'),
           data.get('consult_or_demo'),
           faculty_user.first_name,
           faculty_user.last_name,
           faculty_user.email)

        send_mail(
            subject,
            body,
            faculty_user.email,
            [settings.SERVER_EMAIL])

    def create_course(self, form, affil):
        # Create the course.
        studentaffil = re.sub(r'\.fc\.', '.st.', affil.name)
        g = Group.objects.get_or_create(name=studentaffil)[0]
        fg = Group.objects.get_or_create(name=affil.name)[0]

        c = Course.objects.create(
            group=g,
            faculty_group=fg,
            title=form.cleaned_data.get('course_name'))

        # Add the current user as an instructor.
        c.faculty_group.user_set.add(self.request.user)
        c.add_detail('instructor',
                     get_public_name(self.request.user, self.request))

        # Get the year and term from the affil string.
        affil_dict = {}
        if hasattr(settings, 'COURSEAFFILS_COURSESTRING_MAPPER'):
            affil_dict = settings.COURSEAFFILS_COURSESTRING_MAPPER.to_dict(
                affil.name)
        if affil_dict:
            c.info.year = affil_dict.get('year')
            c.info.term = affil_dict.get('term')
            c.info.save()

    def get_context_data(self, *args, **kwargs):
        context = super(AffilActivateView, self).get_context_data(
            *args, **kwargs)
        pk = self.kwargs.get('pk')
        self.affil = Affil.objects.get(pk=pk)
        affil_dict = self.affil.to_dict()

        studentaffil = re.sub(r'\.fc\.', '.st.', self.affil.name)
        g = Group.objects.filter(name=studentaffil).first()
        if Course.objects.filter(group=g).exists():
            c = Course.objects.filter(group=g).first()
            # If a Course already exists for this group, show an error.
            msg = ('The {} affil is already connected to the course:'
                   ' <strong><a href="/?set_course={}">{}</a></strong>'.format(
                       studentaffil,
                       c.group.name,
                       c))
            messages.error(self.request, mark_safe(msg))
        context.update({
            'affil': self.affil,
            'term': affil_dict['term'],
            'year': affil_dict['year'],
        })
        return context

    def form_valid(self, form):
        pk = self.kwargs.get('pk')
        self.affil = Affil.objects.get(pk=pk)
        self.affil.activated = True
        self.affil.save()

        self.create_course(form, self.affil)

        try:
            self.send_faculty_email(form, self.request.user)
        except SMTPRecipientsRefused:
            messages.error(self.request, 'Failed to send faculty email.')

        try:
            self.send_staff_email(form, self.request.user)
        except SMTPRecipientsRefused:
            messages.error(self.request, 'Failed to send staff email.')

        return super(AffilActivateView, self).form_valid(form)


class ClearTestCache(View):
    def get(self, request, *args, **kwargs):
        # for selenium test use only
        if hasattr(settings, 'LETTUCE_DJANGO_APP'):
            cache.clear()
            ContentType.objects.clear_cache()

        return HttpResponse()
