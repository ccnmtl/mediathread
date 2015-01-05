from courseaffils.lib import in_course, in_course_or_404
from courseaffils.models import Course
from courseaffils.views import available_courses_query
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.template import loader
from django.template.context import Context
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import FormView
from djangohelpers.lib import rendered_with, allow_http
from mediathread.api import UserResource, CourseInfoResource
from mediathread.assetmgr.api import AssetResource
from mediathread.assetmgr.models import Asset, SupportedSource
from mediathread.discussions.utils import get_course_discussions
from mediathread.djangosherd.models import SherdNote
from mediathread.main import course_details
from mediathread.main.course_details import cached_course_is_faculty
from mediathread.main.forms import RequestCourseForm
from mediathread.main.models import UserSetting
from mediathread.mixins import ajax_required, faculty_only, \
    AjaxRequiredMixin, JSONResponseMixin, LoggedInFacultyMixin
from mediathread.projects.api import ProjectResource
from mediathread.projects.models import Project
from restclient import POST
from structuredcollaboration.models import Collaboration
import json
import operator


# returns important setting information for all web pages.
def django_settings(request):
    whitelist = ['PUBLIC_CONTACT_EMAIL',
                 'CONTACT_US_DESTINATION',
                 'FLOWPLAYER_SWF_LOCATION',
                 'FLOWPLAYER_AUDIO_PLUGIN',
                 'FLOWPLAYER_PSEUDOSTREAMING_PLUGIN',
                 'FLOWPLAYER_RTMP_PLUGIN',
                 'DEBUG',
                 'REVISION',
                 'DATABASES',
                 'GOOGLE_ANALYTICS_ID'
                 ]

    context = {'settings': dict([(k, getattr(settings, k, None))
                                 for k in whitelist]),
               'EXPERIMENTAL': 'experimental' in request.COOKIES}

    if request.course:
        context['is_course_faculty'] = request.course.is_faculty(request.user)

    return context


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

    archives = []
    upload_archive = None
    for item in course.asset_set.archives().order_by('title'):
        archive = item.sources['archive']
        thumb = item.sources.get('thumb', None)
        description = item.metadata().get('description', '')
        uploader = item.metadata().get('upload', 0)

        archive_context = {
            "id": item.id,
            "title": item.title,
            "thumb": (None if not thumb else {"id": thumb.id,
                                              "url": thumb.url}),
            "archive": {"id": archive.id, "url": archive.url},
            "metadata": (description[0]
                         if hasattr(description, 'append') else description)
        }

        if (uploader[0] if hasattr(uploader, 'append') else uploader):
            upload_archive = archive_context
        else:
            archives.append(archive_context)

    archives.sort(key=operator.itemgetter('title'))

    owners = []
    if (in_course(logged_in_user.username, request.course) and
        (logged_in_user.is_staff or
         logged_in_user.has_perm('assetmgr.can_upload_for'))):
        owners = UserResource().render_list(request, request.course.members)

    context = {
        'classwork_owner': classwork_owner,
        'help_homepage_instructor_column': False,
        'help_homepage_classwork_column': False,
        'upgrade_bookmarklet': UserSetting.get_setting(
            logged_in_user, "upgrade_bookmarklet", True),
        'faculty_feed': Project.objects.faculty_compositions(request, course),
        'is_faculty': course.is_faculty(logged_in_user),
        'discussions': get_course_discussions(course),
        'msg': request.GET.get('msg', ''),
        'view': request.GET.get('view', ''),
        'archives': archives,
        'upload_archive': upload_archive,
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


@allow_http("GET")
@login_required
@rendered_with('assetmgr/upgrade_bookmarklet.html')
def upgrade_bookmarklet(request):
    context = {}
    if getattr(settings, 'DJANGOSHERD_FLICKR_APIKEY', None):
        # MUST only contain string values for now!!
        # (see templates/assetmgr/bookmarklet.js to see why or fix)
        context['bookmarklet_vars'] = {
            'flickr_apikey': settings.DJANGOSHERD_FLICKR_APIKEY
        }
    return context


@allow_http("GET", "POST")
@rendered_with('dashboard/class_manage_sources.html')
@faculty_only
def class_manage_sources(request):
    key = course_details.UPLOAD_PERMISSION_KEY

    course = request.course
    user = request.user

    upload_enabled = False
    for item in course.asset_set.archives().order_by('title'):
        attribute = item.metadata().get('upload', 0)
        value = attribute[0] if hasattr(attribute, 'append') else attribute
        if value and int(value) == 1:
            upload_enabled = True
            break

    context = {
        'asset_request': request.GET,
        'course': course,
        'supported_archives': SupportedSource.objects.all().order_by("title"),
        'space_viewer': request.user,
        'is_staff': request.user.is_staff,
        'newsrc': request.GET.get('newsrc', ''),
        'delsrc': request.GET.get('delsrc', ''),
        'upload_enabled': upload_enabled,
        'permission_levels': course_details.UPLOAD_PERMISSION_LEVELS,
        'help_video_upload': UserSetting.get_setting(
            user, "help_video_upload", True),
        'help_supported_collections': UserSetting.get_setting(
            user, "help_supported_collections", True),
        'help_dashboard_nav_actions': UserSetting.get_setting(
            user, "help_dashboard_nav_actions", False),
        'help_dashboard_nav_reports': UserSetting.get_setting(
            user, "help_dashboard_nav_reports", False)
    }

    if request.method == "GET":
        context[key] = int(course.get_detail(
            key, course_details.UPLOAD_PERMISSION_DEFAULT))
    else:
        upload_permission = request.POST.get(key)
        request.course.add_detail(key, upload_permission)
        context['changes_saved'] = True
        context[key] = int(upload_permission)

    return context


@allow_http("GET", "POST")
@login_required
@rendered_with('dashboard/class_settings.html')
@faculty_only
def class_settings(request):
    course = request.course
    user = request.user

    context = {
        'asset_request': request.GET,
        'course': course,
        'space_viewer': request.user,
        'is_staff': request.user.is_staff,
        'help_public_compositions': UserSetting.get_setting(
            user, "help_public_compositions", True),
        'help_selection_visibility': UserSetting.get_setting(
            user, "help_selection_visibility", True),
    }

    public_composition_key = course_details.ALLOW_PUBLIC_COMPOSITIONS_KEY
    context[course_details.ALLOW_PUBLIC_COMPOSITIONS_KEY] = int(
        course.get_detail(public_composition_key,
                          course_details.ALLOW_PUBLIC_COMPOSITIONS_DEFAULT))

    selection_visibility_key = course_details.SELECTION_VISIBILITY_KEY
    context[course_details.SELECTION_VISIBILITY_KEY] = int(
        course.get_detail(selection_visibility_key,
                          course_details.SELECTION_VISIBILITY_DEFAULT))

    if request.method == "POST":
        if selection_visibility_key in request.POST:
            selection_visibility_value = \
                int(request.POST.get(selection_visibility_key))
            request.course.add_detail(selection_visibility_key,
                                      selection_visibility_value)
            context[selection_visibility_key] = selection_visibility_value

        if public_composition_key in request.POST:
            public_composition_value = \
                int(request.POST.get(public_composition_key))
            request.course.add_detail(public_composition_key,
                                      public_composition_value)
            context[public_composition_key] = public_composition_value

            if public_composition_value == 0:
                # Check any existing projects -- if they are
                # world publishable, turn this feature OFF
                projects = Project.objects.filter(course=course)
                for project in projects:
                    try:
                        col = Collaboration.objects.get_for_object(project)
                        if col._policy.policy_name == 'PublicEditorsAreOwners':
                            col.policy = 'CourseProtected'
                            col.save()
                    except:
                        pass

        context['changes_saved'] = True

    return context


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
    return HttpResponse(json_stream, mimetype='application/json')


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
        for user in self.request.course.faculty.all():
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
                not request.course.is_faculty(owner)):
            json_stream = json.dumps({
                'success': False,
                'message': '%s is not a course member or faculty member'})
            return HttpResponse(json_stream, mimetype='application/json')

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

        return HttpResponse(json_stream, mimetype='application/json')


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
        notes = SherdNote.objects.get_related_notes(assets, None, faculty)

        ares = AssetResource(include_annotations=False)
        asset_ctx = ares.render_list(request, None, assets, notes)

        projects = Project.objects.by_course_and_users(course, faculty)

        # filter private projects
        collabs = Collaboration.objects.get_for_object_list(projects)
        collabs = collabs.exclude(
            _policy__policy_name='PrivateEditorsAreOwners')
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
        form_data = form.cleaned_data
        form_data.pop('captcha')

        form_data['title'] = 'Mediathread Course Request'
        form_data['pid'] = "514"
        form_data['mid'] = "3596"
        form_data['type'] = 'action item'
        form_data['owner'] = 'ellenm'
        form_data['assigned_to'] = 'ellenm'

        template = loader.get_template('main/course_request_description.txt')
        form_data['description'] = template.render(Context(form_data))

        POST("https://pmt.ccnmtl.columbia.edu/drf/external_add_item/",
             params=form_data, async=True)

        return super(RequestCourseView, self).form_valid(form)
