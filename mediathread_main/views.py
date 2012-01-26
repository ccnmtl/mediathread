from tagging.models import Tag
from tagging.utils import calculate_cloud

from assetmgr.lib import most_popular, annotated_by, get_active_filters

from courseaffils.lib import get_public_name
from courseaffils.lib import in_course_or_404
from courseaffils.models import Course
from djangosherd.models import DiscussionIndex

from djangohelpers.lib import rendered_with
from djangohelpers.lib import allow_http
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.core.urlresolvers import reverse
import datetime
from django.db.models import get_model, Q
from discussions.utils import get_discussions

from mediathread_main.models import UserSetting

import course_details
import simplejson
import re

from clumper import Clumper
from django.conf import settings


from courseaffils.lib import users_in_course
from reports.views import is_unanswered_assignment

ThreadedComment = get_model('threadedcomments', 'threadedcomment')
Collaboration = get_model('structuredcollaboration', 'collaboration')
CollaborationPolicyRecord = get_model('structuredcollaboration', 'collaborationpolicyrecord')
Asset = get_model('assetmgr', 'asset')
SherdNote = get_model('djangosherd', 'sherdnote')
Project = get_model('projects', 'project')
ProjectVersion = get_model('projects', 'projectversion')
User = get_model('auth', 'user')
#for portal
Comment = get_model('comments', 'comment')
ContentType = get_model('contenttypes', 'contenttype')
SupportedSource = get_model('assetmgr', 'supportedsource')
        
#returns important setting information for all web pages.
def django_settings(request):
    whitelist = ['PUBLIC_CONTACT_EMAIL',
                 'FLOWPLAYER_SWF_LOCATION',
                 'DEBUG',
                 'REVISION'
                 ]

    rv = {'settings':dict([(k, getattr(settings, k, None)) for k in whitelist]),
          'EXPERIMENTAL':request.COOKIES.has_key('experimental'),
          }
    if request.course:
        rv['is_course_faculty'] = request.course.is_faculty(request.user)

    return rv


def get_prof_feed(course, request):
    prof_feed = {'assets':[], #assets.filter(c.faculty_filter).order_by('-added'),
                 'projects':[], # we'll add these directly below, to ensure security filters
                 'assignments':[],
                 'tags':Tag.objects.get_for_object(course)
                 }
    prof_projects = Project.objects.filter(
        course.faculty_filter).order_by('title')
    for project in prof_projects:
        if project.class_visible():
            if project.is_assignment(request):
                prof_feed['assignments'].append(project)
            else:
                prof_feed['projects'].append(project)

    #prof_feed['tag_cloud'] = calculate_cloud(prof_feed['tags'])
    prof_feed['show'] = (prof_feed['assets'] or prof_feed['projects'] or prof_feed['assignments'] or prof_feed['tags'])
    return prof_feed

@rendered_with('dashboard/notifications.html')
@allow_http("GET")
def notifications(request):
    c = request.course

    if not c:
        return HttpResponseRedirect('/accounts/login/')

    user = request.user
    if user.is_staff and request.GET.has_key('as'):
        user = get_object_or_404(User, username=request.GET['as'])

    class_feed = []

    #personal feed
    my_assets = {}
    for n in SherdNote.objects.filter(author=user, asset__course=c):
        my_assets[str(n.asset_id)] = 1
    for comment in Comment.objects.filter(user=user):
        if c == getattr(comment.content_object, 'course', None):
            my_assets[str(comment.object_pk)] = 1
    my_discussions = [d.collaboration_id for d in DiscussionIndex.objects
                      .filter(participant=user,
                              collaboration__context=request.collaboration_context
                              )]

    my_feed = Clumper(Comment.objects
                    .filter(content_type=ContentType.objects.get_for_model(Asset),
                            object_pk__in=my_assets.keys())
                    .order_by('-submit_date'), #so the newest ones show up
                    SherdNote.objects.filter(asset__in=my_assets.keys(),
                                             #no global annotations
                                             #warning: if we include global annotations
                                             #we need to stop it from autocreating one on-view
                                             #of the asset somehow
                                             range1__isnull=False
                                             )
                    .order_by('-added'),
                    Project.objects
                    .filter(Q(participants=user.pk) | Q(author=user.pk), course=c)
                    .order_by('-modified'),
                    DiscussionIndex.with_permission(request,
                                                    DiscussionIndex.objects
                                                    .filter(Q(Q(asset__in=my_assets.keys())
                                                              | Q(collaboration__in=my_discussions)
                                                              | Q(collaboration__user=request.user)
                                                              | Q(collaboration__group__user=request.user),
                                                              participant__isnull=False
                                                              )
                                                       )
                                                       .order_by('-modified')
                                                    ),
                    )

    tags = Tag.objects.usage_for_queryset(
        SherdNote.objects.filter(asset__course=c),
        counts=True)

    #only top 10 tags
    tag_cloud = calculate_cloud(sorted(tags, lambda t, w:cmp(w.count, t.count))[:10])

    return {
        'my_feed':my_feed,
        'tag_cloud': tag_cloud,
        'space_viewer': user,
        "help_notifications": UserSetting.get_setting(user, "help_notifications", True)
    }
    
def remove_record(request, user_name, asset_id):
    if not request.is_ajax():
        raise Http404()
    
    in_course_or_404(user_name, request.course)

    asset = get_object_or_404(Asset, pk=asset_id,
                              course=request.course)
    user = get_object_or_404(User, username=user_name)

    if user != request.user:
        return HttpResponseForbidden("forbidden")

    annotations = asset.sherdnote_set.filter(author=user)

    context = {}
    if request.method == "DELETE":
        annotations.delete()
        { 'delete': True }
    

    json_stream = simplejson.dumps(context)
    return HttpResponse(json_stream, mimetype='application/json')

def date_filter_for(attr):

    def date_filter(asset, date_range, user):
        """
        we want the added/modified date *for the user*, ie when the
        user first/last edited/created an annotation on the asset --
        not when the asset itself was created/modified.

        this is really really ugly.  wouldn't be bad in sql but i don't
        trust my sql well enough. after i write some tests maybe?
        """
        if attr == "added":
            annotations = SherdNote.objects.filter(asset=asset, author=user)
            annotations = annotations.order_by('added')
            # get the date on which the earliest annotation was created
            date = annotations[0].added

        elif attr == "modified":
            annotations = SherdNote.objects.filter(asset=asset, author=user)
            # get the date on which the most recent annotation was created
            annotations = annotations.order_by('-added')
            added_date = annotations[0].added
            # also get the most recent modification date of any annotation
            annotations = annotations.order_by('-modified')
            modified_date = annotations[0].modified

            if added_date > modified_date:
                date = added_date
            else:
                date = modified_date

        date = datetime.date(date.year, date.month, date.day)

        today = datetime.date.today()

        if date_range == 'today':
            return date == today
        if date_range == 'yesterday':
            before_yesterday = today + datetime.timedelta(-2)
            return date > before_yesterday and date < today
        if date_range == 'lastweek':
            over_a_week_ago = today + datetime.timedelta(-8)
            return date > over_a_week_ago
    return date_filter

filter_by = {
    'tag': lambda asset, tag, user: filter(lambda x: x.name == tag,
                                           asset.tags()),
    'added': date_filter_for('added'),
    'modified': date_filter_for('modified'),
    }

@rendered_with('homepage.html')
def triple_homepage(request):
    c = request.course

    if not c:
        return HttpResponseRedirect('/accounts/login/')

    user = request.user
    if request.GET.has_key('username'):
        user_name = request.GET['username']
        in_course_or_404(user_name, c)
        user = get_object_or_404(User, username=user_name)
    elif user.is_staff and request.GET.has_key('as'):
        user = get_object_or_404(User, username=request.GET['as'])
        
    #bad language, we should change this to user_of_assets or something
    space_viewer = request.user 
    if request.GET.has_key('as') and request.user.is_staff:
        space_viewer = get_object_or_404(User, username=request.GET['as'])   

    user_records = {
       'space_viewer': space_viewer,
       'space_owner' : user,
       "help_homepage_instructor_column": UserSetting.get_setting(user, "help_homepage_instructor_column", True),
       "help_homepage_classwork_column":  UserSetting.get_setting(user, "help_homepage_classwork_column", True)
    }
    prof_feed = get_prof_feed(c, request)
    discussions = get_discussions(c)

    full_prof_list = []
    for lis in (prof_feed['projects'], prof_feed['assignments'], discussions,):
        full_prof_list.extend(lis)
    full_prof_list.sort(lambda a, b:cmp(a.title.lower(), b.title.lower()))
    
    user_records.update(
        {'faculty_feed':prof_feed,
         'instructor_full_feed':full_prof_list,
         'is_faculty':c.is_faculty(user),
         'display':{'instructor':prof_feed['show'],
                    'course': (len(prof_feed['tags']) < 5)
                    },
         'discussions' : discussions,
         'msg': request.GET.get('msg', ''),
         'tag': request.GET.get('tag', ''),
         'view': request.GET.get('view', '')
         })
    return user_records
    

@allow_http("GET")
def your_records(request, user_name):
    if not request.is_ajax():
        raise Http404()
    
    c = request.course
    in_course_or_404(user_name, c)
    user = get_object_or_404(User, username=user_name)
    
    return get_records(user, c, request)

@allow_http("GET")
def all_records(request):
    if not request.is_ajax():
        raise Http404()
    
    c = request.course
    
    if not request.user.is_staff:
        in_course_or_404(request.user.username, c)
    
    return get_records('all', c, request);
    
def get_records(user, course, request):
    c = course
    today = datetime.date.today()

    editable = (user == request.user)
    
    #bad language, we should change this to user_of_assets or something
    space_viewer = request.user 
    if request.GET.has_key('as') and request.user.is_staff:
        space_viewer = get_object_or_404(User, username=request.GET['as'])
    
    assignments = []
    responder = None
    
    if user == 'all':
        archives = list(course.asset_set.archives())
        assets = [a for a in Asset.objects.filter(course=c).extra(
            select={'lower_title': 'lower(assetmgr_asset.title)'}
            ).select_related().order_by('lower_title')
              if a not in archives]
        user = None
        
        all_tags = Tag.objects.usage_for_queryset(
            SherdNote.objects.filter(
                asset__course=course),
            counts=True)
        all_tags.sort(lambda a, b:cmp(a.name.lower(), b.name.lower()))
        tags = calculate_cloud(all_tags)
        
        projects = [p for p in Project.objects.filter(course=c,
                                                      submitted=True).order_by('title')
                                                      if p.visible(request)]
    else:
        assets = annotated_by(Asset.objects.filter(course=c),
                          user,
                          include_archives=c.is_faculty(user)
                          )
        
        tags = calculate_cloud(Tag.objects.usage_for_queryset(
        user.sherdnote_set.filter(
            asset__course=c),
        counts=True))
                
        projects = Project.get_user_projects(user, c).order_by('-modified')
        if not editable:
            projects = [p for p in projects if p.visible(request)]

        project_type = ContentType.objects.get_for_model(Project)
        assignments = []
        maybe_assignments = Project.objects.filter(
            c.faculty_filter)
        for assignment in maybe_assignments:
            if not assignment.visible(request):
                continue
            if assignment in projects:
                continue
            if is_unanswered_assignment(assignment, user, request, project_type):
                assignments.append(assignment)
        
        if user.id == space_viewer.id:
            responder = space_viewer.username
    
    for fil in filter_by:
        filter_value = request.GET.get(fil)
        if filter_value:
            assets = [asset for asset in assets
                      if filter_by[fil](asset, filter_value, user)]
    
    active_filters = get_active_filters(request, filter_by)
    
    asset_json = []
    for asset in assets:
        the_json = asset.sherd_json(request)
        gannotation, created = SherdNote.objects.global_annotation(asset, user or space_viewer, auto_create=False)
        if gannotation:
            the_json['global_annotation'] = gannotation.sherd_json(request, 'x', ('tags', 'body'))
            
        the_json['editable'] = editable
            
        annotations = []
        if request.GET.has_key('annotations'):
            # @todo: refactor this serialization into a common place.
            def author_name(request, annotation, key):
                if not annotation.author_id:
                    return None
                return 'author_name', get_public_name(annotation.author, request)
            def primary_type(request, annotation, key):
                return "primary_type", asset.primary.label
            for ann in asset.sherdnote_set.filter(range1__isnull=False, author=user):
                annotations.append(ann.sherd_json(request, 'x', ('title', 'author', 'tags', author_name, 'body', 'modified', 'timecode', primary_type)))
            the_json['annotations'] = annotations
            
        asset_json.append(the_json)
        
    project_json = []
    for p in projects:
        the_json = {}
        the_json['id'] = p.id
        the_json['title'] = p.title
        the_json['url'] = p.get_absolute_url()
        
        participants = p.attribution_list()
        the_json['authors'] = [ {'name': get_public_name(u, request) } for u in participants]
        the_json['modified'] = p.modified.strftime("%m/%d/%y %I:%M %p")
        the_json['status'] = p.status()
        the_json['editable'] = editable
        
        feedback = p.feedback_discussion()
        if feedback:
            the_json['feedback'] = feedback.id
        
        collaboration = p.collaboration()
        if collaboration:
            collaboration_parent = collaboration.get_parent()
            if collaboration_parent:
                the_json['collaboration'] = {}
                the_json['collaboration']['title'] = collaboration_parent.title
                if collaboration_parent.content_object:
                    the_json['collaboration']['url'] = collaboration_parent.content_object.get_absolute_url()
        
        project_json.append(the_json)

    data = {'assets': asset_json,
            'assignments' : [ {'id': a.id, 'responder': responder, 'url': a.get_absolute_url(), 'title': a.title, 'modified': a.modified.strftime("%m/%d/%y %I:%M %p")} for a in assignments],
            'projects' : project_json,
            'tags': [ { 'name': tag.name } for tag in tags ],
            'active_filters': active_filters,
            'space_viewer'  : { 'username': space_viewer.username, 'public_name': get_public_name(space_viewer, request), 'can_manage': (space_viewer.is_staff and not user) },
            'editable' : editable,
            'owners' : [{ 'username': m.username, 'public_name': get_public_name(m, request) } for m in request.course.members],
            'compositions' : len(projects) > 0 or len(assignments) > 0,
            'is_faculty': c.is_faculty(space_viewer),
           }
    
    if user:
        data['space_owner'] = { 'username': user.username, 'public_name': get_public_name(user, request) }

    json_stream = simplejson.dumps(data, indent=2)
    return HttpResponse(json_stream, mimetype='application/json')

@allow_http("GET", "POST")
@rendered_with('dashboard/dashboard_home.html')
def dashboard(request):
    user = request.user
    
    return { 
       "space_viewer": request.user,
       "help_dashboard_nav_actions": UserSetting.get_setting(user, "help_dashboard_nav_actions", True),
       "help_dashboard_nav_reports": UserSetting.get_setting(user, "help_dashboard_nav_reports", True)      
    }

@allow_http("GET", "POST")
@rendered_with('dashboard/class_addsource.html')
def class_addsource(request):
    import operator
    
    key = course_details.UPLOAD_PERMISSION_KEY
    
    c = request.course
    user = request.user
    if not request.course.is_faculty(user):
        return HttpResponseForbidden("forbidden")
    
    upload_enabled = False
    for a in c.asset_set.archives().order_by('title'):
        attribute = a.metadata().get('upload', 0)
        value = attribute[0] if hasattr(attribute, 'append') else attribute
        if value and int(value) == 1:
            upload_enabled = True
            break
        
    context = {
            'asset_request': request.GET,
            'course': c,
            'supported_archives': SupportedSource.objects.all().order_by("title"), # sort by title
            'space_viewer': request.user,
            'is_staff': request.user.is_staff,
            'newsrc' : request.GET.get('newsrc', ''),
            'upload_enabled': upload_enabled,
            'permission_levels': course_details.UPLOAD_PERMISSION_LEVELS,
            'help_video_upload': UserSetting.get_setting(user, "help_video_upload", True),
            'help_supported_collections': UserSetting.get_setting(user, "help_supported_collections", True),
            'help_dashboard_nav_actions': UserSetting.get_setting(user, "help_dashboard_nav_actions", True),
            'help_dashboard_nav_reports': UserSetting.get_setting(user, "help_dashboard_nav_reports", True)
        }

    if request.method == "GET":
        context[key] = int(c.get_detail(key, course_details.UPLOAD_PERMISSION_DEFAULT))    
    else:
        upload_permission = request.POST.get(key)
        request.course.add_detail(key, upload_permission)
        context['changes_saved'] = True
        context[key] = int(upload_permission)
            
    return context

@allow_http("GET", "POST")
@rendered_with('dashboard/class_settings.html')
def class_settings(request):
    import operator
    
    c = request.course
    user = request.user
    if not request.course.is_faculty(user):
        return HttpResponseForbidden("forbidden")
    
    context = {
            'asset_request': request.GET,
            'course': c,
            'space_viewer': request.user,
            'is_staff': request.user.is_staff,
            'help_public_compositions': UserSetting.get_setting(user, "help_public_compositions", True),
    }
    
    key = course_details.ALLOW_PUBLIC_COMPOSITIONS_KEY
    context[course_details.ALLOW_PUBLIC_COMPOSITIONS_KEY] = int(c.get_detail(key, course_details.ALLOW_PUBLIC_COMPOSITIONS_DEFAULT))
    
    if request.method == "POST":
        value = int(request.POST.get(key))
        request.course.add_detail(key, value)
        context['changes_saved'] = True
        context[key] = value
        
        if value == 0:
            # Check any existing projects -- if they are world publishable, turn this feature OFF
            projects = Project.objects.filter(course=c)
            for p in projects:
                col = Collaboration.get_associated_collab(p)
                if col._policy.policy_name == 'PublicEditorsAreOwners':
                    col.policy = 'CourseProtected'
                    col.save()
                
    return context

@allow_http("POST")
def set_user_setting(request, user_name):
    if not request.is_ajax():
        raise Http404()
    
    user = get_object_or_404(User, username=user_name)
    name = request.POST.get("name")
    value = request.POST.get("value")
    
    UserSetting.set_setting(user, name, value)
    
    json_stream = simplejson.dumps({ 'success': True })
    return HttpResponse(json_stream, mimetype='application/json')
