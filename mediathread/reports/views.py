from courseaffils.lib import users_in_course
from courseaffils.models import Course
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models.aggregates import Count
from django.db.models.query_utils import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from djangohelpers.lib import allow_http, rendered_with
from mediathread.assetmgr.models import Asset
from mediathread.discussions.utils import get_course_discussions
from mediathread.djangosherd.models import DiscussionIndex, SherdNote
from mediathread.main import course_details
from mediathread.main.clumper import Clumper
from mediathread.mixins import faculty_only
from mediathread.projects.models import Project
from mediathread.taxonomy.models import Vocabulary, TermRelationship
from structuredcollaboration.models import Collaboration
from tagging.models import Tag
import csv
import re
import json


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

    context = {'students': students, 'submenu': 'summary', }
    if request.user.is_staff:
        context['courses'] = Course.objects.all()
    return context


@allow_http("GET")
@faculty_only
def class_summary_graph(request):

    # groups: 1=domains,2=assets,3=projects
    the_context = {'nodes': [], 'links': []}

    assets = {}  # [ann_asset.id] = index
    projects = {}  # [a_project.id] = {index:0}
    users = {}  # {projects:[],assets:[]}
    discussions = {}

    # domains --> assets
    for ann_asset in Asset.objects.filter(course=request.course):
        try:
            domain = re.search('://([^/]+)/',
                               ann_asset.primary.url).groups()[0]
        except:
            continue

        the_context['nodes'].append({'nodeName': "%s (%s)" % (ann_asset.title,
                                                              domain),
                                     'group': 2,
                                     'href': ann_asset.get_absolute_url(),
                                     'domain': domain, })
        assets[ann_asset.id] = len(the_context['nodes']) - 1

    # projects
    for a_project in Project.objects.filter(course=request.course):
        p_users = a_project.participants.all()
        p_node = {'nodeName': a_project.title,
                  'group': 3,
                  'href': a_project.get_absolute_url(),
                  'users': dict([(user.username, 1) for user in p_users]), }
        the_context['nodes'].append(p_node)
        projects[a_project.id] = {'index': len(the_context['nodes']) - 1,
                                  'assets': {}, }

        for user in p_users:
            if request.course.is_faculty(user):
                p_node['faculty'] = True
            users.setdefault(user.username,
                             {'projects': []})['projects'].append(a_project.id)

        # projects-->assets
        for ann in a_project.citations():
            ann_asset = projects[a_project.id]['assets'].setdefault(
                ann.asset_id, {'str': 2, 'bare': False})
            ann_asset['str'] = ann_asset['str'] + 1
            ann_asset['bare'] = (ann_asset['bare'] or ann.is_null())
        for a_id, val in projects[a_project.id]['assets'].items():
            if not a_id in assets:
                continue

            the_context['links'].append({
                'source': projects[a_project.id]['index'],
                'target': assets[a_id],
                'value': val['str'],
                'bare': val['bare'], })
    # comments
    collaboration_context = request.collaboration_context
    proj_type = ContentType.objects.get_for_model(Project)

    for didx in DiscussionIndex.objects.filter(
        collaboration__context=collaboration_context,
            participant__isnull=False).order_by('-modified'):
        the_context['nodes'].append({
            'nodeName': 'Comment: %s' %
            (didx.participant.get_full_name() or didx.participant.username),
            'users': {didx.participant.username: 1},
            'group': 4,
            'href': didx.get_absolute_url(),
            'faculty': request.course.is_faculty(didx.participant),
        })

        d_ind = len(the_context['nodes']) - 1
        # linking discussions in ann_asset chain
        if didx.collaboration_id in discussions:
            the_context['links'].append({
                'source': d_ind,
                'target': discussions[didx.collaboration_id][-1]})
            discussions[didx.collaboration_id].append(d_ind)
        else:
            discussions[didx.collaboration_id] = [d_ind]
            if (didx.collaboration._parent_id and
                didx.collaboration._parent.content_type == proj_type and
                    int(didx.collaboration._parent.object_pk) in projects):
                the_context['links'].append({
                    'source': d_ind,
                    'target': projects[int(
                        didx.collaboration._parent.object_pk)]['index'], })

        # comment --> asset
        if didx.asset_id:
            the_context['links'].append({'source': d_ind,
                                         'target': assets[didx.asset_id], })

    return HttpResponse(json.dumps(the_context, indent=2),
                        mimetype='application/json')


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

    context = {'my_feed': my_feed, 'submenu': 'activity', }
    if request.user.is_staff:
        context['courses'] = Course.objects.all()
    return context


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
               'Students', '% Active Students',
               'Items', 'Selections',
               'Compositions', 'Assignments', 'Discussions',
               #'# of Discussion Items', '% participating in Discussions',
               'Public To World Compositions', 'All Selections Visible',
               '# of Active Tags', '% Using Tags',
               '% Items Tagged', '% Selections Tagged',
               '# of Active Vocabulary Terms', '% Using Vocabulary',
               '% Items Classified', '% Selections Classified']
    writer.writerow(headers)

    rows = []
    for the_course in Course.objects.all().order_by('-id'):
    #for the_course in Course.objects.filter(id=84):  # ccnmtl internal
        if (the_course.faculty_group is None or
            (not (the_course.faculty_group.name.startswith('t1') or
                  the_course.faculty_group.name.startswith('t2') or
                  the_course.faculty_group.name.startswith('t3')))):
            continue

        row = []
        row.append(the_course.id)
        row.append(the_course.title)

        if 'instructor' in the_course.details():
            row.append(the_course.details()['instructor'].value)
        else:
            row.append('')

        course_string = the_course.faculty_group.name
        row.append(course_string)

        bits = the_course.faculty_group.name.split('.')
        row.append(bits[0])  # term
        row.append(bits[1][1:])  # year
        row.append(bits[2])  # section
        row.append(bits[3])  # courseNo
        row.append(bits[4])  # school

        students = the_course.group.user_set.all()
        if the_course.faculty_group:
            ids = the_course.faculty_group.user_set.values('id')
            students = students.exclude(id__in=ids)
        row.append(len(students))

        if len(students) > 0:
            active = students.filter(Q(projects__isnull=False) |
                                     Q(sherdnote__isnull=False)).distinct()
            row.append(float(len(active)) / len(students) * 100)
        else:
            row.append(0)

        items = Asset.objects.filter(course=the_course)
        row.append(len(items))

        selections = SherdNote.objects.filter(asset__course=the_course)
        row.append(len(selections))

        compositions = 0
        assignments = 0

        projects = Project.objects.filter(course=the_course)
        for project in projects:
            if project.visibility_short() == 'Assignment':
                assignments += 1
            else:
                compositions += 1

        row.append(compositions)
        row.append(assignments)
        try:
            discussions = get_course_discussions(the_course)
            row.append(len(discussions))
            '# of Discussion Items', '% participating in Discussions',
        except Collaboration.DoesNotExist:
            row.append(0)

        row.append(course_details.allow_public_compositions(the_course))
        row.append(course_details.all_selections_are_visible(the_course))

        # Breakdown tags & vocabulary terms by item & selection
        if len(selections) > 0:
            item_notes = selections.filter(range1=None, range2=None)
            sel_notes = selections.exclude(range1=None, range2=None)

            tags = Tag.objects.usage_for_queryset(selections)
            row.append(len(tags))  # # of Active Tags',
            tag_users = len(
                selections.filter(tags__isnull=False).distinct('author'))
            if len(students) > 0:
                # % users using tags
                row.append(float(tag_users) / len(students) * 100)
            else:
                row.append(0)

            #'% Items Tagged', '% Selections Tagged'
            t = item_notes.filter(tags__isnull=False).exclude(tags__exact='')
            row.append(float(len(t)) / len(selections) * 100)
            t = sel_notes.filter(tags__isnull=False).exclude(tags__exact='')
            row.append(float(len(t)) / len(selections) * 100)

            # Vocabulary
            vocab = Vocabulary.objects.get_for_object(the_course)
            content_type = ContentType.objects.get_for_model(SherdNote)
            related = TermRelationship.objects.filter(
                term__vocabulary__in=vocab,
                content_type=content_type,
                object_id__in=selections.values_list('id'))

            # '# of Active Vocabulary Terms'
            q = related.aggregate(Count('term', distinct=True))
            active_terms = q['term__count']
            vocab_users = len(SherdNote.objects.filter(
                id__in=related.values_list('object_id')).distinct(
                'author'))

            row.append(active_terms)
            if len(students) > 0:
                row.append(float(vocab_users) / len(students) * 100)  # % users
            else:
                row.append(0)

            related_ids = related.values_list('object_id')
            items = len(SherdNote.objects.filter(id__in=related_ids,
                                                 range1=None, range2=None))
            row.append(float(items) / len(selections) * 100)  # % Items
            sel = len(SherdNote.objects.filter(id__in=related_ids).exclude(
                range1=None, range2=None))
            row.append(float(sel) / len(selections) * 100)  # % Selections

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
    for the_course in Course.objects.all().order_by('-id'):
        if not (the_course.faculty_group.name.startswith('t1') or
                the_course.faculty_group.name.startswith('t2') or
                the_course.faculty_group.name.startswith('t3')):
            continue

        bits = the_course.faculty_group.name.split('.')
        school = bits[4]

        if not school in rows:
            row = [school, 0, 0, 0, 0, 0]
            rows[school] = row

        items = Asset.objects.filter(course=the_course)
        rows[school][1] += len(items)

        selections = SherdNote.objects.filter(asset__course=the_course)
        rows[school][2] += len(selections)

        compositions = 0
        assignments = 0

        projects = Project.objects.filter(course=the_course)
        for project in projects:
            if project.visibility_short() == 'Assignment':
                assignments += 1
            else:
                compositions += 1

        rows[school][3] += compositions
        rows[school][4] += assignments
        try:
            rows[school][5] += len(get_course_discussions(the_course))
        except Collaboration.DoesNotExist:
            pass  # no discussions exist, that's ok

    for row in rows.values():
        try:
            writer.writerow(row)
        except:
            pass

    return response
