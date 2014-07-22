from courseaffils.lib import in_course, in_course_or_404
from courseaffils.views import available_courses_query
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from djangohelpers.lib import rendered_with, allow_http
from mediathread.api import UserResource
from mediathread.assetmgr.models import Asset, SupportedSource
from mediathread.discussions.utils import get_course_discussions
from mediathread.main import course_details
from mediathread.main.models import UserSetting
from mediathread.mixins import ajax_required, faculty_only
from mediathread.projects.models import Project
from structuredcollaboration.models import Collaboration
import operator
import json


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
               'EXPERIMENTAL': 'experimental' in request.COOKIES, }

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
                        col = Collaboration.get_associated_collab(project)
                        if col._policy.policy_name == 'PublicEditorsAreOwners':
                            col.policy = 'CourseProtected'
                            col.save()
                    except:
                        pass

        context['changes_saved'] = True

    return context


@allow_http("POST")
@rendered_with('dashboard/class_settings.html')
@ajax_required
def set_user_setting(request, user_name):
    user = get_object_or_404(User, username=user_name)
    name = request.POST.get("name")
    value = request.POST.get("value")

    UserSetting.set_setting(user, name, value)

    json_stream = json.dumps({'success': True})
    return HttpResponse(json_stream, mimetype='application/json')


@allow_http("GET", "POST")
@rendered_with('dashboard/class_migrate.html')
@login_required
@faculty_only
def migrate(request):
    if request.method == "GET":
        # Only show courses for which the user is an instructor
        available_courses = available_courses_query(request.user)
        courses = []
        if request.user.is_superuser:
            courses = available_courses
        else:
            for course in available_courses:
                if course.is_faculty(request.user):
                    courses.append(course)

        # Only send down the real faculty. Not all us staff members
        faculty = []
        for user in request.course.faculty.all():
            faculty.append(user)

        return {
            "current_course_faculty": faculty,
            "available_courses": courses,
            "help_migrate_materials": False
        }
    elif request.method == "POST":
        # maps old ids to new objects
        object_map = {'assets': {},
                      'notes': {},
                      'note_count': 0,
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

        if 'asset_set' in request.POST:
            asset_set = json.loads(request.POST.get('asset_set'))
            object_map = Asset.objects.migrate(asset_set,
                                               request.course,
                                               owner,
                                               object_map)

        if 'project_set' in request.POST:
            project_set = json.loads(request.POST.get('project_set'))
            object_map = Project.objects.migrate(project_set,
                                                 request.course,
                                                 owner,
                                                 object_map)

        json_stream = json.dumps({
            'success': True,
            'asset_count': len(object_map['assets']),
            'project_count': len(object_map['projects']),
            'note_count': object_map['note_count']})
        return HttpResponse(json_stream, mimetype='application/json')
