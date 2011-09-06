from tagging.models import Tag
from tagging.utils import calculate_cloud

from assetmgr.lib import most_popular, annotated_by, get_active_filters

from courseaffils.lib import get_public_name
from courseaffils.lib import in_course_or_404
from courseaffils.models import Course
from djangosherd.models import DiscussionIndex
from djangosherd.models import SherdNote

from djangohelpers.lib import rendered_with
from djangohelpers.lib import allow_http
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.core.urlresolvers import reverse
import datetime
from django.db.models import get_model,Q
from discussions.utils import get_discussions

from django.utils import simplejson as json
import re

from clumper import Clumper
from django.conf import settings

from courseaffils.lib import users_in_course
from reports.views import is_unanswered_assignment

ThreadedComment = get_model('threadedcomments', 'threadedcomment')
Collaboration = get_model('structuredcollaboration', 'collaboration')
Asset = get_model('assetmgr','asset')
SherdNote = get_model('djangosherd','sherdnote')
Project = get_model('projects','project')
ProjectVersion = get_model('projects','projectversion')
User = get_model('auth','user')
#for portal
Comment = get_model('comments','comment')
ContentType = get_model('contenttypes','contenttype')
        
#returns important setting information for all web pages.
def django_settings(request):
    whitelist = ['PUBLIC_CONTACT_EMAIL',
                 'FLOWPLAYER_SWF_LOCATION',
                 'DEBUG',
                 ]

    rv = {'settings':dict([(k,getattr(settings,k,None)) for k in whitelist]),
          'EXPERIMENTAL':request.COOKIES.has_key('experimental'),
          }
    if request.course:
        rv['is_course_faculty'] = request.course.is_faculty(request.user)

    return rv


def get_prof_feed(course,request):
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

@rendered_with('projects/notifications.html')
@allow_http("GET")
def notifications(request):
    c = request.course

    if not c:
        return HttpResponseRedirect('/accounts/login/')

    user = request.user
    if user.is_staff and request.GET.has_key('as'):
        user = get_object_or_404(User,username=request.GET['as'])

    class_feed =[]

    #personal feed
    my_assets = {}
    for n in SherdNote.objects.filter(author=user,asset__course=c):
        my_assets[str(n.asset_id)] = 1
    for comment in Comment.objects.filter(user=user):
        if c == getattr(comment.content_object,'course',None):
            my_assets[str(comment.object_pk)] = 1
    my_discussions = [d.collaboration_id for d in DiscussionIndex.objects
                      .filter(participant=user,
                              collaboration__context=request.collaboration_context
                              )]

    my_feed=Clumper(Comment.objects
                    .filter(content_type=ContentType.objects.get_for_model(Asset),
                            object_pk__in = my_assets.keys())
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
                    .filter(Q(participants=user.pk)|Q(author=user.pk), course=c)
                    .order_by('-modified'),
                    DiscussionIndex.with_permission(request,
                                                    DiscussionIndex.objects
                                                    .filter(Q(Q(asset__in=my_assets.keys())
                                                              |Q(collaboration__in=my_discussions)
                                                              |Q(collaboration__user=request.user)
                                                              |Q(collaboration__group__user=request.user),
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
    tag_cloud = calculate_cloud(sorted(tags,lambda t,w:cmp(w.count,t.count))[:10])

    return {
        'my_feed':my_feed,
        'tag_cloud': tag_cloud,
        }

@rendered_with('projects/portal.html')
@allow_http("GET")
def class_portal(request):
    c = request.course

    if not c:
        return HttpResponseRedirect('/accounts/login/')

    user = request.user
    if user.is_staff and request.GET.has_key('as'):
        user = get_object_or_404(User,username=request.GET['as'])

    #instructor focus
    prof_feed = get_prof_feed(c,request)

    class_feed =[]
    #class_feed=Clumper(SherdNote.objects.filter(asset__course=c,
    #                                            range1__isnull=False),
    #                   Comment.objects.filter(object_pk__in = [str(a.pk) for a in assets],
    #                                          user__in = [u.pk for u in c.members ]),
    #                   assets.order_by('-added')[:6],
    #                   Project.objects.filter(course=c,
    #                                          submitted=True).order_by('-modified')[:6]
    #                   )
    #personal feed
    my_assets = {}
    for n in SherdNote.objects.filter(author=user,asset__course=c):
        my_assets[str(n.asset_id)] = 1
    for comment in Comment.objects.filter(user=user):
        if c == getattr(comment.content_object,'course',None):
            my_assets[str(comment.object_pk)] = 1
    my_discussions = [d.collaboration_id for d in DiscussionIndex.objects
                      .filter(participant=user,
                              collaboration__context=request.collaboration_context
                              )]

    my_feed=Clumper(Comment.objects
                    .filter(content_type=ContentType.objects.get_for_model(Asset),
                            object_pk__in = my_assets.keys())
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
                    .filter(Q(participants=user.pk)|Q(author=user.pk), course=c)
                    .order_by('-modified'),
                    DiscussionIndex.with_permission(request,
                                                    DiscussionIndex.objects
                                                    .filter(Q(Q(asset__in=my_assets.keys())
                                                              |Q(collaboration__in=my_discussions)
                                                              |Q(collaboration__user=request.user)
                                                              |Q(collaboration__group__user=request.user),
                                                              participant__isnull=False
                                                              )
                                                       )
                                                       .order_by('-modified')
                                                    ),
                    )
    #latest_saves = assets.order_by('-added')
    #popular_assets = most_popular(assets)

    tags = Tag.objects.usage_for_queryset(
        SherdNote.objects.filter(asset__course=c),
        counts=True)
    #tag_cloud = calculate_cloud(tags)
    #only top 10 tags
    tag_cloud = calculate_cloud(sorted(tags,lambda t,w:cmp(w.count,t.count))[:10])

    display = {'instructor':prof_feed['show'],
               'course': (len(prof_feed['tags']) < 5 or
                          len(class_feed) >9 ),
               }
         
         
    
    discussions = get_discussions(c)
       
    #TODO: move this into a nice class method.
    #coll = ContentType.objects.get_for_model(Collaboration)
    #discussions = [d for d in ThreadedComment.objects.filter(parent=None, content_type = coll) if d.content_object.get_parent().content_object == c]



    
    return {
        'is_faculty':c.is_faculty(user),
        'faculty_feed':prof_feed,
        #'class_feed':class_feed,
        'my_feed':my_feed,
        'display':display,
        'discussions' : discussions,
        'course_id' : c.id,
        #'new_assets':latest_saves,
        #'popular_assets': popular_assets,
        'tag_cloud': tag_cloud,
        }


@allow_http("DELETE")
def remove_record(request, user_name, asset_id):

    in_course_or_404(user_name, request.course)

    asset = get_object_or_404(Asset, pk=asset_id,
                              course=request.course)
    user = get_object_or_404(User, username=user_name)

    if user != request.user:
        return HttpResponseForbidden("forbidden")

    annotations = asset.sherdnote_set.filter(author=user)

    if request.method == "DELETE":
        annotations.delete()
        return HttpResponseRedirect(
            reverse('your-space-records', args=[user_name]))


@allow_http("GET")
def your_space(request, user_name):
    
    in_course_or_404(user_name, request.course)

    return HttpResponseRedirect(reverse('your-space-records',
                                        args=[user_name]))


@allow_http("GET")
@rendered_with('projects/classlisting.html')
def class_listing(request):
    
    students = users_in_course(request.course).order_by('username')
    
    return {
        'students': students
        }




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
    if user.is_staff and request.GET.has_key('as'):
        user = get_object_or_404(User,username=request.GET['as'])

    user_records = get_records(user, c, request)
    prof_feed = get_prof_feed(c, request)
    discussions = get_discussions(c)

    full_prof_list = []
    for lis in (prof_feed['projects'], prof_feed['assignments'], discussions, ):
        full_prof_list.extend(lis)
    full_prof_list.sort(lambda a,b:cmp(a.title.lower(),b.title.lower()))

    user_records.update(
        {'faculty_feed':prof_feed,
         'instructor_full_feed':full_prof_list,
         'is_faculty':c.is_faculty(user),         
         'display':{'instructor':prof_feed['show'],
                    'course': (len(prof_feed['tags']) < 5)
                    },
         'discussions' : discussions,
         })
    return user_records
    

@allow_http("GET")
@rendered_with('projects/your_records.html')
def your_records(request, user_name):
    c = request.course
    in_course_or_404(user_name, c)
    user = get_object_or_404(User, username=user_name)
    
    return get_records(user, c, request)

@allow_http("GET")
def all_records(request):
    c = request.course
    in_course_or_404(request.user.username, c)
    
    return get_records('all', c, request);
    
def get_records(user, course, request):
    c = course
    today = datetime.date.today()

    editable = (user==request.user)
    
    if user == 'all':
        archives = list(course.asset_set.archives())
        assets = [a for a in Asset.objects.filter(course=course).extra(
            select={'lower_title': 'lower(assetmgr_asset.title)'}
            ).select_related().order_by('lower_title')
              if a not in archives]
        user = None
    else:
        assets = annotated_by(Asset.objects.filter(course=c),
                          user,
                          include_archives=c.is_faculty(user)
                          )

    
    if user:
        tags = calculate_cloud(Tag.objects.usage_for_queryset(
                user.sherdnote_set.filter(
                    asset__course=c),
                counts=True))
    else:
        all_tags = Tag.objects.usage_for_queryset(
            SherdNote.objects.filter(
                asset__course=course),
            counts=True)
        all_tags.sort(lambda a,b:cmp(a.name.lower(),b.name.lower()))
        tags = calculate_cloud(all_tags)
        
    
    for fil in filter_by:
        filter_value = request.GET.get(fil)
        if filter_value:
            assets = [asset for asset in assets
                      if filter_by[fil](asset, filter_value, user)]
    
    active_filters = get_active_filters(request, filter_by)
    
    #bad language, we should change this to user_of_assets or something
    space_viewer = request.user 
    if request.GET.has_key('as') and request.user.is_staff:
        space_viewer = get_object_or_404(User, username=request.GET['as'])
    
    if request.is_ajax():
        asset_json = []
        for asset in assets:
            the_json = asset.sherd_json(request)
            gannotation, created = SherdNote.objects.global_annotation(asset, user or space_viewer, auto_create=False)
            if gannotation:
                the_json['global_annotation'] = gannotation.sherd_json(request, 'x', ('tags','body') )
                
            the_json['editable'] = editable
                
            annotations = []
            if request.GET.has_key('annotations'):
                # @todo: refactor this serialization into a common place.
                def author_name(request, annotation, key):
                    if not annotation.author_id:
                        return None
                    return 'author_name',get_public_name(annotation.author, request)
                for ann in asset.sherdnote_set.filter(range1__isnull=False,author=user):
                    annotations.append( ann.sherd_json(request, 'x', ('title','author','tags',author_name,'body','modified', 'timecode') ) )
                the_json['annotations'] = annotations
                
            asset_json.append(the_json)

        data = {'assets': asset_json,
                'tags': [ { 'name': tag.name } for tag in tags ],
                'active_filters': active_filters,
                'space_viewer'  : { 'username': space_viewer.username, 'public_name': get_public_name(space_viewer, request), 'can_manage': (space_viewer.is_staff and not user) },
                'editable'      : editable,
                'owners' : [{ 'username': m.username, 'public_name': get_public_name(m, request) } for m in request.course.members],
               }
        
        if user:
            data['space_owner'] = { 'username': user.username, 'public_name': get_public_name(user, request) }
    
        json_stream = json.dumps(data, indent=2)
        return HttpResponse(json_stream, mimetype='application/json')
    else:
        dates = (('today','today'),
             ('yesterday','yesterday'),
             ('lastweek','within the last week'),)    
            
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
        
        return {
            'assets'        : assets,
            'assignments'   : assignments,
            'projects'      : projects,
            'tags'          : tags,
            'dates'         : dates,
            'space_owner'   : user,
            'space_viewer'  : space_viewer,
            'editable'      : editable,
            'active_filters': active_filters,
            }


@allow_http("GET")
@rendered_with('slide.html')
def base_slide(request):
    return {}
