from datetime import datetime
import json

from courseaffils.lib import in_course_or_404, in_course
from courseaffils.middleware import SESSION_KEY
from courseaffils.models import Course
from courseaffils.views import available_courses_query
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.template import loader
from django.template.context import Context
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from djangohelpers.lib import rendered_with, allow_http
import requests
from threadedcomments.models import ThreadedComment

from lti_auth.models import LTICourseContext
from mediathread.api import UserResource, CourseInfoResource
from mediathread.assetmgr.api import AssetResource
from mediathread.assetmgr.models import Asset, SuggestedExternalCollection, \
    ExternalCollection
from mediathread.discussions.utils import get_course_discussions
from mediathread.djangosherd.models import SherdNote
from mediathread.main import course_details
from mediathread.main.course_details import cached_course_is_faculty, \
    course_information_title
from mediathread.main.forms import RequestCourseForm, ContactUsForm, \
    CourseDeleteMaterialsForm
from mediathread.main.models import UserSetting
from mediathread.mixins import ajax_required, \
    AjaxRequiredMixin, JSONResponseMixin, LoggedInFacultyMixin, \
    LoggedInSuperuserMixin
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
def triple_homepage(request):
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


class CourseSettingsView(LoggedInFacultyMixin, TemplateView):
    template_name = 'dashboard/class_settings.html'

    def get_context_data(self, **kwargs):

        context = {'course': self.request.course}

        key = course_details.ALLOW_PUBLIC_COMPOSITIONS_KEY
        context[key] = int(self.request.course.get_detail(key,
                           course_details.ALLOW_PUBLIC_COMPOSITIONS_DEFAULT))

        key = course_details.ITEM_VISIBILITY_KEY
        context[key] = int(self.request.course.get_detail(key,
                           course_details.ITEM_VISIBILITY_DEFAULT))

        key = course_details.SELECTION_VISIBILITY_KEY
        context[key] = int(self.request.course.get_detail(key,
                           course_details.SELECTION_VISIBILITY_DEFAULT))

        key = course_details.COURSE_INFORMATION_TITLE_KEY
        context[key] = self.request.course.get_detail(
            key, course_details.COURSE_INFORMATION_TITLE_DEFAULT)

        context['lti_context'] = LTICourseContext.objects.filter(
            group=self.request.course.group.id,
            faculty_group=self.request.course.faculty_group.id).first()

        return context

    def post(self, request):
        key = course_details.COURSE_INFORMATION_TITLE_KEY
        if key in request.POST:
            value = request.POST.get(key)
            request.course.add_detail(key, value)

        key = course_details.ITEM_VISIBILITY_KEY
        if key in request.POST:
            value = int(request.POST.get(key))
            request.course.add_detail(key, value)

            key = course_details.SELECTION_VISIBILITY_KEY
            if key in request.POST:
                value = int(request.POST.get(key))
            else:
                value = 0

            request.course.add_detail(key, value)

            if value == 0:
                Project.objects.limit_response_policy(request.course)

        key = course_details.ALLOW_PUBLIC_COMPOSITIONS_KEY
        if key in request.POST:
            value = int(request.POST.get(key))
            request.course.add_detail(key, value)

            if value == 0:
                Project.objects.reset_publish_to_world(request.course)

        messages.add_message(request, messages.INFO,
                             'Your changes were saved.')

        return HttpResponseRedirect(reverse('course-settings'))


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
        available_courses = available_courses_query(self.request.user)
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
            # POST back to the user. Assumes task or support emails are set.
            tmpl = loader.get_template('main/contact_email_response.txt')
            send_mail(subject, tmpl.render(Context(form_data)),
                      settings.SERVER_EMAIL, (form_data['email'],))
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


class CoursePromoteUserView(LoggedInFacultyMixin, View):

    def post(self, request):
        student_id = request.POST.get('student_id', None)
        student = get_object_or_404(User, id=student_id)
        request.course.faculty_group.user_set.add(student)

        msg = '{} is now faculty'.format(student.get_full_name())
        messages.add_message(request, messages.INFO, msg)

        return HttpResponseRedirect(reverse('course-roster'))


class CourseDemoteUserView(LoggedInFacultyMixin, View):

    def post(self, request):
        faculty_id = request.POST.get('faculty_id', None)
        faculty = get_object_or_404(User, id=faculty_id)
        request.course.faculty_group.user_set.remove(faculty)

        msg = '{} is now a student'.format(faculty.get_full_name())
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

        msg = '{} is no longer a course member'.format(user.get_full_name())
        messages.add_message(request, messages.INFO, msg)

        return HttpResponseRedirect(reverse('course-roster'))
