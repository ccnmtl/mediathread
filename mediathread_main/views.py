from tagging.models import Tag
from tagging.utils import calculate_cloud

from assetmgr.lib import most_popular, annotated_by, get_active_filters

from courseaffils.lib import in_course_or_404
from courseaffils.models import Course
from djangosherd.models import DiscussionIndex

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

import simplejson as json
import re

from clumper import Clumper
from django.conf import settings

from courseaffils.lib import users_in_course

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
                 'FLOWPLAYER_SWF_LOCATION',]

    return {'settings':dict([(k,getattr(settings,k,None)) for k in whitelist]),
            'EXPERIMENTAL':request.COOKIES.has_key('experimental')
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

    assets = Asset.objects.filter(course=c)
    #instructor focus
    prof_feed = {'assets':[], #assets.filter(c.faculty_filter).order_by('-added'),
                 'projects':Project.objects.filter(c.faculty_filter,
                                                   submitted=True
                                                   ).order_by('title'),
                 'tags':Tag.objects.get_for_object(c)
                 }
    #prof_feed['tag_cloud'] = calculate_cloud(prof_feed['tags'])
    if prof_feed['assets'] or prof_feed['projects'] or prof_feed['tags']:
        prof_feed['show'] = True

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
                                                              |Q(collaboration__group__user=request.user)
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

    display = {'instructor':(len(prof_feed['projects'])+len(prof_feed['assets'])),
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


@allow_http("GET")
@rendered_with('projects/class_summary.html')
def class_summary(request):
    """FACULTY ONLY reporting of entire class activity """
    if not request.course.is_faculty(request.user):
        return HttpResponseForbidden("forbidden")
        
    students = []
    for stud in users_in_course(request.course).order_by('last_name','first_name','username'):
        students.append({
                'get_full_name':stud.get_full_name(),
                'username':stud.username,
                'annotations':SherdNote.objects.filter(asset__course=request.course,
                                                       author=stud).count(),
                'projects':Project.get_user_projects(stud,request.course).count(),
                'comments':DiscussionIndex.objects.filter(participant=stud,collaboration__context=request.collaboration_context).count()
                })

    my_feed=Clumper(
        SherdNote.objects.filter(asset__course=request.course).order_by('-added')[:40],
        Project.objects.filter(course=request.course).order_by('-modified')[:40],
        DiscussionIndex.objects.filter(
            collaboration__context=request.collaboration_context).order_by('-modified')[:40],
        )
    
    rv = {
        'students': students,
        'my_feed':my_feed,
        }
    if request.user.is_staff:
        rv['courses'] = Course.objects.all()
    return rv

@allow_http("GET")
def class_summary_graph(request):
    """FACULTY ONLY reporting of class activity graph """
    if not request.course.is_faculty(request.user):
        return HttpResponseForbidden("forbidden")
    rv = {'nodes':[],#groups: 1=domains,2=assets,3=projects
          'links':[]}

    domains = {} #{index:0, assets:[{ind1},ind2]}
    assets = {}
    projects = {}
    users= {} #{projects:[],assets:[]}
    discussions = {}

    #domains --> assets
    for a in Asset.objects.filter(course=request.course):
        try: 
            domain = re.search('://([^/]+)/',a.primary.url).groups()[0]
        except: continue

        if not domains.has_key(domain):
        #    rv['nodes'].append({'nodeName':domain,'group':1})
            domains[domain] = {'internal':len(domains),
                               #'index':len(rv['nodes'])-1,
                               }
        rv['nodes'].append({'nodeName':a.title,
                            'group':2,
                            'id':a.id,
                            'domain':domain,
                            })
        assets[a.id] = len(rv['nodes'])-1
        #rv['links'].append({'source':domains[domain]['index'],
        #                    'target':assets[a.id],
        #                    'value':10,
        #                    })

    #projects --> assets
    for p in Project.objects.filter(course=request.course):
        rv['nodes'].append({'nodeName':p.title,'group':3,'id':p.id})
        projects[p.id] = {'index':len(rv['nodes'])-1,
                          'assets':{}
                          }
        for ann in p.citations():
            try: ann.asset
            except: continue
            a = projects[p.id]['assets'].setdefault(ann.asset.id,
                                                    {'str':2,
                                                     'bare':False
                                                     })
            a['str']=a['str']+1
            a['bare']=(a['bare'] or ann.is_null())
        for a_id,v in projects[p.id]['assets'].items():
            if not assets.has_key(a_id): continue
            rv['links'].append({'source':projects[p.id]['index'],
                                'target':assets[a_id],
                                'value':v['str'],
                                'bare':v['bare'],
                                })
    #comments --> assets
    c = request.collaboration_context
    for di in DiscussionIndex.objects.filter(collaboration__context=c).order_by('-modified'):
        rv['nodes'].append({'nodeName':'Comment: %s' % (di.participant.get_full_name() or di.participant.username),
                            'group':4,
                           })
        d_ind = len(rv['nodes'])-1
        if di.asset_id:
            rv['links'].append({'source':d_ind,
                                'target':assets[di.asset_id],
                                'value':1,
                                })
        
    return HttpResponse(json.dumps(
            rv, 
            indent=2), mimetype='application/json')



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



@allow_http("GET")
@rendered_with('projects/your_records.html')
def your_records(request, user_name):

    c = request.course
    in_course_or_404(user_name, c)

    today = datetime.date.today()
    user = get_object_or_404(User, username=user_name)

    editable = (user==request.user)
    assets = annotated_by(Asset.objects.filter(course=c),
                          user,
                          include_archives=c.is_faculty(user)
                          )

    projects = Project.get_user_projects(user, c).order_by('-modified')
    if not editable:
        projects = [p for p in projects if p.visible(request)]


    for fil in filter_by:
        filter_value = request.GET.get(fil)
        if filter_value:
            assets = [asset for asset in assets
                      if filter_by[fil](asset, filter_value, user)]

    tags = calculate_cloud(Tag.objects.usage_for_queryset(
            user.sherdnote_set.filter(
                asset__course=c),
            counts=True))
    
    active_filters = get_active_filters(request, filter_by)
    #bad language, we should change this to user_of_assets or something
    space_viewer = request.user 
    if request.GET.has_key('as') and request.user.is_staff:
        space_viewer = get_object_or_404(User, username=request.GET['as'])

    return {
        'assets'        : assets,
        'projects'      : projects,
        'tags'          : tags,
        'dates'         : (('today','today'),
                           ('yesterday','yesterday'),
                           ('lastweek','within the last week'),
                           ),
        'space_owner'   : user,
        'space_viewer'  : space_viewer,
        'editable'      : editable,
        'active_filters': active_filters,
        }


