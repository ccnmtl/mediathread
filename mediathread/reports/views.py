from courseaffils.lib import users_in_course
from courseaffils.models import Course
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from djangohelpers.lib import allow_http, rendered_with
from mediathread.assetmgr.models import Asset
from mediathread.discussions.utils import get_course_discussions
from mediathread.djangosherd.models import DiscussionIndex, SherdNote
from mediathread.main import course_details
from mediathread.main.clumper import Clumper
from mediathread.main.decorators import faculty_only
from mediathread.projects.models import Project
from structuredcollaboration.models import Collaboration
import csv
import re
import simplejson as json


@allow_http("GET")
@rendered_with('dashboard/class_assignment_report.html')
@faculty_only
def class_assignment_report(request, project_id):
    assignment = get_object_or_404(Project, id=project_id)
    responses = assignment.responses(request)
    return {'assignment': assignment,
            'responses': responses, }


@allow_http("GET")
@rendered_with('dashboard/class_assignments.html')
@faculty_only
def class_assignments(request):
    assignments = []
    maybe_assignments = Project.objects.filter(
        request.course.faculty_filter)
    for assignment in maybe_assignments:
        if assignment.is_assignment(request):
            assignments.append(assignment)

    num_students = users_in_course(request.course).count()
    return {'assignments': sorted(assignments,
                                  key=lambda assignment: assignment.title),
            'num_students': num_students,
            'submenu': 'assignments', }


@allow_http("GET")
@rendered_with('dashboard/class_summary.html')
@faculty_only
def class_summary(request):
    collab_context = request.collaboration_context
    students = []
    for stud in users_in_course(request.course).order_by('last_name',
                                                         'first_name',
                                                         'username'):

        stud.__dict__.update({
            'annotations':
            SherdNote.objects.filter(asset__course=request.course,
                                     author=stud).count(),
            'all_projects':
            len(Project.objects.visible_by_course_and_user(
                request, request.course, stud)),

            # 'project_adds':stud_work.get(stud.id,[0,0])[0],
            # 'project_deletes':stud_work.get(stud.id,[0,0])[1],
            'comments':
            DiscussionIndex.objects.filter(
                participant=stud,
                collaboration__context=collab_context).count()
        })
        students.append(stud)

    rv = {'students': students, 'submenu': 'summary', }
    if request.user.is_staff:
        rv['courses'] = Course.objects.all()
    return rv


@allow_http("GET")
@faculty_only
def class_summary_graph(request):

    # groups: 1=domains,2=assets,3=projects
    rv = {'nodes': [], 'links': []}

    assets = {}  # [a.id] = index
    projects = {}  # [p.id] = {index:0}
    users = {}  # {projects:[],assets:[]}
    discussions = {}

    # domains --> assets
    for a in Asset.objects.filter(course=request.course):
        try:
            domain = re.search('://([^/]+)/', a.primary.url).groups()[0]
        except:
            continue

        rv['nodes'].append({'nodeName': "%s (%s)" % (a.title, domain),
                            'group': 2,
                            'href': a.get_absolute_url(),
                            'domain': domain, })
        assets[a.id] = len(rv['nodes']) - 1

    # projects
    for p in Project.objects.filter(course=request.course):
        p_users = p.participants.all()
        p_node = {'nodeName': p.title,
                  'group': 3,
                  'href': p.get_absolute_url(),
                  'users': dict([(u.username, 1) for u in p_users]), }
        rv['nodes'].append(p_node)
        projects[p.id] = {'index': len(rv['nodes']) - 1, 'assets': {}, }

        for u in p_users:
            if request.course.is_faculty(u):
                p_node['faculty'] = True
            users.setdefault(u.username,
                             {'projects': []})['projects'].append(p.id)

        # projects-->assets
        for ann in p.citations():
            a = projects[p.id]['assets'].setdefault(ann.asset_id,
                                                    {'str': 2, 'bare': False})
            a['str'] = a['str'] + 1
            a['bare'] = (a['bare'] or ann.is_null())
        for a_id, v in projects[p.id]['assets'].items():
            if not a_id in assets:
                continue

            rv['links'].append({'source': projects[p.id]['index'],
                                'target': assets[a_id],
                                'value': v['str'],
                                'bare': v['bare'], })
    # comments
    c = request.collaboration_context
    proj_type = ContentType.objects.get_for_model(Project)

    for di in DiscussionIndex.objects.filter(
        collaboration__context=c,
            participant__isnull=False).order_by('-modified'):
        rv['nodes'].append({
            'nodeName': 'Comment: %s' %
            (di.participant.get_full_name() or di.participant.username),
            'users': {di.participant.username: 1},
            'group': 4,
            'href': di.get_absolute_url(),
            'faculty': request.course.is_faculty(di.participant),
        })

        d_ind = len(rv['nodes']) - 1
        # linking discussions in a chain
        if di.collaboration_id in discussions:
            rv['links'].append({'source': d_ind,
                                'target': discussions[di.collaboration_id][-1],
                                })
            discussions[di.collaboration_id].append(d_ind)
        else:
            discussions[di.collaboration_id] = [d_ind]
            if (di.collaboration._parent_id and
                di.collaboration._parent.content_type == proj_type and
                    int(di.collaboration._parent.object_pk) in projects):
                rv['links'].append({
                    'source': d_ind,
                    'target': projects[int(
                        di.collaboration._parent.object_pk)]['index'], })

        # comment --> asset
        if di.asset_id:
            rv['links'].append({'source': d_ind,
                                'target': assets[di.asset_id], })

    return HttpResponse(json.dumps(rv, indent=2), mimetype='application/json')


@allow_http("GET")
@rendered_with('dashboard/class_activity.html')
@faculty_only
def class_activity(request):
    collab_context = request.collaboration_context

    my_feed = Clumper(
        SherdNote.objects.filter(
            asset__course=request.course).order_by('-added')[:40],
        Project.objects.filter(course=request.course,
                               submitted=True).order_by('-modified')[:40],
        DiscussionIndex.with_permission(
            request, DiscussionIndex.objects.filter(
                collaboration__context=collab_context)
            .order_by('-modified')[:40],))

    rv = {'my_feed': my_feed, 'submenu': 'activity', }
    if request.user.is_staff:
        rv['courses'] = Course.objects.all()
    return rv


@login_required
def mediathread_activity_by_course(request):
    """STAFF ONLY reporting of entire application activity """
    if not request.user.is_staff:
        return HttpResponseForbidden("forbidden")

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = \
        'attachment; filename=mediathread_activity_by_course.csv'
    writer = csv.writer(response)
    headers = ['Id', 'Title', 'Instructor', 'Course String',
               'Term', 'Year', 'Section', 'Course Number', 'School',
               'Students', 'Items', 'Selections',
               'Compositions', 'Assignments', 'Discussions',
               'Public To World Compositions',
               'All Selections Visible']
    writer.writerow(headers)

    rows = []
    for c in Course.objects.all().order_by('-id'):
        if not (c.faculty_group.name.startswith('t1') or
                c.faculty_group.name.startswith('t2') or
                c.faculty_group.name.startswith('t3')):
            continue

        row = []
        row.append(c.id)
        row.append(c.title)

        if 'instructor' in c.details():
            row.append(c.details()['instructor'].value)
        else:
            row.append('')

        course_string = c.faculty_group.name
        row.append(course_string)

        bits = c.faculty_group.name.split('.')
        row.append(bits[0])  # term
        row.append(bits[1][1:])  # year
        row.append(bits[2])  # section
        row.append(bits[3])  # courseNo
        row.append(bits[4])  # school
        row.append(len(c.students))

        items = Asset.objects.filter(course=c)
        row.append(len(items))

        selections = SherdNote.objects.filter(asset__course=c)
        row.append(len(selections))

        compositions = 0
        assignments = 0

        projects = Project.objects.filter(course=c)
        for p in projects:
            if p.visibility_short() == 'Assignment':
                assignments += 1
            else:
                compositions += 1

        row.append(compositions)
        row.append(assignments)
        try:
            row.append(len(get_course_discussions(c)))
        except Collaboration.DoesNotExist:
            row.append(0)

        row.append(course_details.allow_public_compositions(c))
        row.append(course_details.all_selections_are_visible(c))

        rows.append(row)

    for row in rows:
        try:
            writer.writerow(row)
        except:
            pass

    return response


@login_required
def mediathread_activity_by_school(request):
    """STAFF ONLY reporting of entire application activity """
    if not request.user.is_staff:
        return HttpResponseForbidden("forbidden")

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = \
        'attachment; filename=mediathread_activity_by_school.csv'
    writer = csv.writer(response)
    headers = ['School', 'Items', 'Selections',
               'Compositions', 'Assignments', 'Discussions']
    writer.writerow(headers)

    rows = {}
    for c in Course.objects.all().order_by('-id'):
        if not (c.faculty_group.name.startswith('t1') or
                c.faculty_group.name.startswith('t2') or
                c.faculty_group.name.startswith('t3')):
            continue

        bits = c.faculty_group.name.split('.')
        school = bits[4]

        if not school in rows:
            row = [school, 0, 0, 0, 0, 0]
            rows[school] = row

        items = Asset.objects.filter(course=c)
        rows[school][1] += len(items)

        selections = SherdNote.objects.filter(asset__course=c)
        rows[school][2] += len(selections)

        compositions = 0
        assignments = 0

        projects = Project.objects.filter(course=c)
        for p in projects:
            if p.visibility_short() == 'Assignment':
                assignments += 1
            else:
                compositions += 1

        rows[school][3] += compositions
        rows[school][4] += assignments
        try:
            rows[school][5] += len(get_course_discussions(c))
        except Collaboration.DoesNotExist:
            pass  # no discussions exist, that's ok

    for row in rows.values():
        try:
            writer.writerow(row)
        except:
            pass

    return response
