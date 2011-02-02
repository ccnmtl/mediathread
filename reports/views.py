from courseaffils.lib import in_course_or_404
from courseaffils.lib import users_in_course

from courseaffils.models import Course
from djangosherd.models import DiscussionIndex

from djangohelpers.lib import rendered_with
from djangohelpers.lib import allow_http
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.db.models import get_model,Q

import simplejson as json
import re

from mediathread_main.clumper import Clumper

Asset = get_model('assetmgr','asset')
SherdNote = get_model('djangosherd','sherdnote')
Project = get_model('projects','project')
ContentType = get_model('contenttypes','contenttype')



def is_assignment(assignment, request):
    collab = assignment.collaboration()
    if not collab: 
        # Who knows what it is
        return False

    if not collab.permission_to("add_child", request):
        # It must not be an assignment
        return False 

    return True

def is_unanswered_assignment(assignment, user, request, expected_type):
    if not is_assignment(assignment, request):
        return False

    collab = assignment.collaboration()
    children = collab.children.all()
    if not children:
        # It has no responses, but it looks like an assignment
        return True

    for child in children:
        if child.content_type != expected_type:
            # Ignore this child, it isn't a project
            continue
        if child.content_object.author == user:
            # Aha! We've answered it already
            return False

    # We are an assignment; we have children; 
    # we haven't found a response by the target user.
    return True


@allow_http("GET")
@rendered_with('reports/class_assignment_report.html')
def class_assignment_report(request, id):
    assignment = get_object_or_404(Project, id=id)
    responses = assignment.responses(request)
    return {
        'assignment': assignment,
        'responses': responses,
        }

@allow_http("GET")
@rendered_with('reports/class_assignments.html')
def class_assignments(request):
    if not request.course.is_faculty(request.user):
        return HttpResponseForbidden("forbidden")
    
    project_type = ContentType.objects.get_for_model(Project)
    assignments = []
    maybe_assignments = Project.objects.filter(
        request.course.faculty_filter)
    for assignment in maybe_assignments:
        if is_assignment(assignment, request):
            assignments.append(assignment)
            
    num_students = users_in_course(request.course).count()
    return {
        'assignments': assignments,
        'num_students': num_students,
        'submenu':'assignments',
        }

@allow_http("GET")
@rendered_with('reports/class_summary.html')
def class_summary(request):
    """FACULTY ONLY reporting of entire class activity """
    if not request.course.is_faculty(request.user):
        return HttpResponseForbidden("forbidden")
        
    stud_work = {}
    for p in Project.objects.filter(course=request.course):
        for stud_id, contribs in p.content_metrics().items():
            stud_work.setdefault(stud_id,[0,0])
            stud_work[stud_id][0] += contribs[0]
            stud_work[stud_id][1] += contribs[1]


    students = []
    for stud in users_in_course(request.course).order_by('last_name','first_name','username'):
        students.append({
                'id':stud.id,
                'get_full_name':stud.get_full_name(),
                'username':stud.username,
                'annotations':SherdNote.objects.filter(asset__course=request.course,
                                                       author=stud).count(),
                'projects':Project.get_user_projects(stud,request.course).count(),
                'project_adds':stud_work.get(stud.id,[0,0])[0],
                'project_deletes':stud_work.get(stud.id,[0,0])[1],
                'comments':DiscussionIndex.objects.filter(participant=stud,collaboration__context=request.collaboration_context).count()
            })
        
        

    rv = {
        'students': students,
        'submenu':'summary',
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
    assets = {} # [a.id] = index
    projects = {} #[p.id] = {index:0}
    users= {} #{projects:[],assets:[]}
    discussions = {}

    #domains --> assets
    for a in Asset.objects.filter(course=request.course):
        try: 
            domain = re.search('://([^/]+)/',a.primary.url).groups()[0]
        except: continue
        rv['nodes'].append({'nodeName':"%s (%s)" % (a.title,domain) ,
                            'group':2,
                            'href':a.get_absolute_url(),
                            'domain':domain,
                            })
        assets[a.id] = len(rv['nodes'])-1

    #projects
    for p in Project.objects.filter(course=request.course):
        p_users = p.participants.all()
        p_node = {'nodeName':p.title,
                  'group':3,
                  'href':p.get_absolute_url(),
                  'users':dict([(u.username,1) for u in p_users]), 
                  }
        rv['nodes'].append(p_node)
        projects[p.id] = {'index':len(rv['nodes'])-1,'assets':{},}

        for u in p_users:
            if request.course.is_faculty(u):
                p_node['faculty'] = True
            users.setdefault(u.username,{'projects':[]})['projects'].append(p.id)

        #projects-->assets
        for ann in p.citations():
            a = projects[p.id]['assets'].setdefault(ann.asset_id,
                                                    {'str':2,'bare':False})
            a['str']=a['str']+1
            a['bare']=(a['bare'] or ann.is_null())
        for a_id,v in projects[p.id]['assets'].items():
            if not assets.has_key(a_id): continue
            rv['links'].append({'source':projects[p.id]['index'],
                                'target':assets[a_id],
                                'value':v['str'],
                                'bare':v['bare'],
                                })
    #comments
    c = request.collaboration_context
    proj_type = ContentType.objects.get_for_model(Project)

    for di in DiscussionIndex.objects.filter(collaboration__context=c, 
                                             participant__isnull=False).order_by('-modified'):
        rv['nodes'].append({'nodeName':'Comment: %s' % (di.participant.get_full_name() or di.participant.username),
                            'users':{di.participant.username:1},
                            'group':4,
                            'href':di.get_absolute_url(),
                            'faculty':request.course.is_faculty(di.participant),
                           })
        

        d_ind = len(rv['nodes'])-1
        #linking discussions in a chain
        if discussions.has_key(di.collaboration_id):
            rv['links'].append({'source':d_ind,
                                'target':discussions[di.collaboration_id][-1],
                                })
            discussions[di.collaboration_id].append(d_ind)
        else:
            discussions[di.collaboration_id] = [d_ind]
            if (di.collaboration._parent_id and 
                di.collaboration._parent.content_type==proj_type and
                projects.has_key(int(di.collaboration._parent.object_pk))
                ):
                rv['links'].append({'source':d_ind,
                                    'target':projects[
                            int(di.collaboration._parent.object_pk)]['index'],
                                    })

        #comment --> asset
        if di.asset_id:
            rv['links'].append({'source':d_ind,
                                'target':assets[di.asset_id],
                                })
            
        


    return HttpResponse(json.dumps(
            rv, 
            indent=2), mimetype='application/json')


@allow_http("GET")
@rendered_with('reports/class_activity.html')
def class_activity(request):
    """FACULTY ONLY reporting of entire class activity """
    if not request.course.is_faculty(request.user):
        return HttpResponseForbidden("forbidden")

    my_feed=Clumper(
        SherdNote.objects.filter(asset__course=request.course).order_by('-added')[:40],
        Project.objects.filter(course=request.course).order_by('-modified')[:40],
        DiscussionIndex.objects.filter(
            collaboration__context=request.collaboration_context).order_by('-modified')[:40],
        )

    rv = {
        'my_feed':my_feed,
        'submenu':'activity',
        }
    if request.user.is_staff:
        rv['courses'] = Course.objects.all()
    return rv
