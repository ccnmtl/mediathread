import unicodecsv as csv
import json
import re

from courseaffils.lib import users_in_course
from courseaffils.models import Course
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models.aggregates import Count
from django.db.models.query_utils import Q
from django.http import HttpResponse
from django.http.response import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic.base import View
from djangohelpers.lib import allow_http, rendered_with
from registration.models import RegistrationProfile
from tagging.models import Tag

from mediathread.assetmgr.models import Asset, Source
from mediathread.discussions.utils import get_course_discussions
from mediathread.djangosherd.models import DiscussionIndex, SherdNote
from mediathread.main import course_details
from mediathread.main.clumper import Clumper
from mediathread.main.util import user_display_name
from mediathread.mixins import faculty_only, LoggedInSuperuserMixin, \
    CSVResponseMixin, LoggedInFacultyMixin
from mediathread.projects.models import Project
from mediathread.taxonomy.models import TermRelationship
from structuredcollaboration.models import Collaboration


@allow_http("GET")
@rendered_with('dashboard/class_assignment_report.html')
@faculty_only
def class_assignment_report(request, project_id):
    assignment = get_object_or_404(Project, id=project_id)
    responses = assignment.responses(request.course, request.user)
    return {'assignment': assignment, 'responses': responses}


@allow_http("GET")
@rendered_with('dashboard/class_assignments.html')
@faculty_only
def class_assignments(request):
    assignments = []
    for project in Project.objects.filter(request.course.faculty_filter):
        if project.is_essay_assignment() or project.is_selection_assignment():
            assignments.append(project)

    return {'assignments': sorted(assignments,
                                  key=lambda assignment: assignment.title),
            'num_students': len(request.course.students)}


@allow_http("GET")
@rendered_with('dashboard/class_summary.html')
@faculty_only
def class_summary(request):
    collab_context = request.collaboration_context
    students = []
    for student in users_in_course(request.course).order_by('last_name',
                                                            'first_name',
                                                            'username'):

        student.__dict__.update({
            'annotations':
            SherdNote.objects.filter(asset__course=request.course,
                                     author=student).count(),
            'all_projects':
            len(Project.objects.visible_by_course_and_user(
                request.course, request.user, student, False)),

            'comments':
            DiscussionIndex.objects.filter(
                participant=student,
                collaboration__context=collab_context).count()
        })
        students.append(student)

    context = {'students': students}
    return context


class ClassSummaryGraphView(LoggedInFacultyMixin, View):

    def initialize_assets(self, course):
        # domains --> assets
        for ann_asset in Asset.objects.filter(course=course):
            try:
                match = re.search('://([^/]+)/', ann_asset.primary.url)
            except Source.DoesNotExist:
                continue

            domain = None
            if match:
                groups = match.groups()
                if len(groups) > 0:
                    domain = groups[0]

            self.nodes.append({
                'nodeName': "%s (%s)" % (ann_asset.title, domain),
                'group': 2,
                'href': ann_asset.get_absolute_url(),
                'domain': domain,
            })
            self.assets[ann_asset.id] = len(self.nodes) - 1

    def initialize_discussions(self, course, collaboration_context):
        discussions = {}
        # comments
        collaboration_context = collaboration_context
        proj_type = ContentType.objects.get_for_model(Project)

        for didx in DiscussionIndex.objects.filter(
            collaboration__context=collaboration_context,
                participant__isnull=False).order_by('-modified'):
            self.nodes.append({
                'nodeName':
                    'Comment: %s' % user_display_name(didx.participant),
                'users': {didx.participant.username: 1},
                'group': 4,
                'href': didx.get_absolute_url(),
                'faculty': course.is_faculty(didx.participant),
            })

            d_ind = len(self.nodes) - 1

            # linking discussions in ann_asset chain
            if didx.collaboration_id in discussions:
                self.links.append({
                    'source': d_ind,
                    'target': discussions[didx.collaboration_id][-1]})
                discussions[didx.collaboration_id].append(d_ind)
            else:
                discussions[didx.collaboration_id] = [d_ind]
                if (didx.collaboration._parent_id and
                    didx.collaboration._parent.content_type == proj_type and
                        int(didx.collaboration._parent.object_pk)
                        in self.projects):
                    self.links.append({
                        'source': d_ind,
                        'target': self.projects[int(
                            didx.collaboration._parent.object_pk)]['index']})

            # comment --> asset
            if didx.asset_id and didx.asset_id in self.assets:
                self.links.append({
                    'source': d_ind,
                    'target': self.assets[didx.asset_id]
                })

    def get(self, request, *args, **kwargs):
        self.nodes = []
        self.links = []
        self.assets = {}
        self.projects = {}
        self.discussions = {}
        self.users = {}

        self.initialize_assets(request.course)

        # projects
        for a_project in Project.objects.filter(course=request.course):
            p_users = a_project.participants.all()
            p_node = {'nodeName': a_project.title,
                      'group': 3,
                      'href': a_project.get_absolute_url(),
                      'users': dict([(user.username, 1) for user in p_users])}
            self.nodes.append(p_node)
            self.projects[a_project.id] = {
                'index': len(self.nodes) - 1,
                'assets': {}
            }

            for user in p_users:
                if request.course.is_faculty(user):
                    p_node['faculty'] = True
                self.users.setdefault(
                    user.username,
                    {'projects': []})['projects'].append(a_project.id)

            # projects-->assets
            for ann in a_project.citations():
                ann_asset = self.projects[a_project.id]['assets'].setdefault(
                    ann.asset_id, {'str': 2, 'bare': False})
                ann_asset['str'] = ann_asset['str'] + 1
                ann_asset['bare'] = (ann_asset['bare'] or ann.is_null())

            for a_id, val in self.projects[a_project.id]['assets'].items():
                if a_id not in self.assets:
                    continue

                self.links.append({
                    'source': self.projects[a_project.id]['index'],
                    'target': self.assets[a_id],
                    'value': val['str'],
                    'bare': val['bare'], })

        self.initialize_discussions(request.course,
                                    request.collaboration_context)

        the_context = {'nodes': self.nodes, 'links': self.links}

        return HttpResponse(json.dumps(the_context, indent=2),
                            content_type='application/json')


@allow_http("GET")
@rendered_with('dashboard/class_activity.html')
@faculty_only
def class_activity(request):
    assets = SherdNote.objects.filter(
        asset__course=request.course).order_by('-added')[:40]

    projects = Project.objects.filter(
        course=request.course,
        date_submitted__isnull=False).order_by('-modified')[:40]

    discussions = DiscussionIndex.with_permission(
        request, DiscussionIndex.objects.filter(
            collaboration__context=request.collaboration_context).order_by(
                '-modified')[:40],)

    return {'my_feed': Clumper(assets, projects, discussions)}


class ActivityByCourseView(LoggedInSuperuserMixin, CSVResponseMixin, View):

    date_fmt = "%m/%d/%y %I:%M %p"

    def all_students(self, the_course):
        students = the_course.group.user_set.all()
        if the_course.faculty_group:
            ids = the_course.faculty_group.user_set.values('id')
            students = students.exclude(id__in=ids)
        return students

    def active_students(self, students):
        if len(students) > 0:
            active = students.filter(Q(projects__isnull=False) |
                                     Q(sherdnote__isnull=False)).distinct()
            return float(len(active)) / len(students) * 100
        else:
            return 0

    def discussion_count(self, the_course):
        try:
            discussions = get_course_discussions(the_course)
            return len(discussions)
            '# of Discussion Items', '% participating in Discussions',
        except Collaboration.DoesNotExist:
            return 0

    def project_count(self, the_course):
        compositions = 0
        assignments = 0
        responses = 0

        projects = Project.objects.filter(course=the_course)
        for project in projects:
            if project.is_assignment_type():
                assignments += 1
            elif project.assignment() is not None:
                responses += 1
            else:
                compositions += 1

        return compositions, assignments, responses

    def get(self, request, *args, **kwargs):
        headers = ['Id', 'Created', 'Title', 'Instructor', 'Course String',
                   'Term', 'Year', 'Section', 'Course Number', 'School',
                   'Students', '% Active Students',
                   'Total Items', 'Student Items', 'Student Selections',
                   'Compositions', 'Assignments', 'Responses', 'Discussions',
                   'Public To World Compositions', 'All Selections Visible',
                   '# of Active Tags', '% Using Tags',
                   '% Items Tagged', '% Selections Tagged',
                   '# of Active Vocabulary Terms', '% Using Vocabulary',
                   '% Items Classified', '% Selections Classified']

        rows = []
        # Hard-coding date until we have time to code a proper ui
        qs = Course.objects.filter(
            created_at__year__gte='2019', created_at__month__gte='6')
        for the_course in qs.order_by('-id'):
            row = []
            row.append(the_course.id)
            row.append(the_course.created_at.strftime(self.date_fmt))
            row.append(the_course.title)

            if 'instructor' in the_course.details():
                row.append(the_course.details()['instructor'].value)
            else:
                row.append('')

            course_string = the_course.faculty_group.name
            row.append(course_string)

            bits = the_course.faculty_group.name.split('.')
            if len(bits) >= 5:
                row.append(bits[0])  # term
                row.append(bits[1][1:])  # year
                row.append(bits[2])  # section
                row.append(bits[3])  # courseNo
                row.append(bits[4])  # school
            else:
                row.append('')
                row.append('')
                row.append('')
                row.append('')
                row.append('')

            students = self.all_students(the_course)
            row.append(len(students))
            row.append(self.active_students(students))

            items = Asset.objects.filter(course=the_course)
            row.append(len(items))

            # student work only
            student_ids = students.values('id')
            items = Asset.objects.filter(
                course=the_course, author__id__in=student_ids)
            row.append(len(items))

            selections = SherdNote.objects.filter(
                asset__course=the_course, author__id__in=student_ids)
            row.append(len(selections))

            compositions, assignments, responses = \
                self.project_count(the_course)
            row.append(compositions)
            row.append(assignments)
            row.append(responses)
            row.append(self.discussion_count(the_course))
            row.append(course_details.allow_public_compositions(the_course))
            row.append(course_details.all_selections_are_visible(the_course))

            # Breakdown tags & vocabulary terms by item & selection
            if len(selections) > 0:
                item_notes = selections.filter(range1=None, range2=None)
                sel_notes = selections.exclude(range1=None, range2=None)

                tags = Tag.objects.usage_for_queryset(selections)
                row.append(len(tags))  # # of Active Tags',

                tagged = selections.filter(tags__isnull=False).values('author')
                tag_users = tagged.distinct().count()
                if len(students) > 0:
                    # % users using tags
                    row.append(float(tag_users) / len(students) * 100)
                else:
                    row.append(0)

                # '% Items Tagged', '% Selections Tagged'
                t = item_notes.filter(tags__isnull=False).exclude(
                    tags__exact='')
                row.append(float(len(t)) / len(selections) * 100)
                t = sel_notes.filter(tags__isnull=False).exclude(
                    tags__exact='')
                row.append(float(len(t)) / len(selections) * 100)

                # Vocabulary
                related = TermRelationship.objects.filter(
                    term__vocabulary__course=the_course,
                    sherdnote__id__in=selections.values_list('id', flat=True))

                # '# of Active Vocabulary Terms'
                q = related.aggregate(Count('term', distinct=True))
                active_terms = q['term__count']
                q = related.aggregate(
                    Count('sherdnote__author', distinct=True))
                vocab_users = q['sherdnote__author__count']

                row.append(active_terms)
                if len(students) > 0:
                    # % users
                    row.append(float(vocab_users) / len(students) * 100)
                else:
                    row.append(0)

                related_ids = related.values_list('sherdnote__id', flat=True)
                items = len(SherdNote.objects.filter(id__in=related_ids,
                                                     range1=None, range2=None))
                row.append(float(items) / len(selections) * 100)  # % Items
                sel = len(SherdNote.objects.filter(id__in=related_ids).exclude(
                    range1=None, range2=None))
                row.append(float(sel) / len(selections) * 100)  # % Selections

            rows.append(row)

        return self.render_csv_response(
            'mediathread_activity_by_course', headers, rows)


class SelfRegistrationReportView(LoggedInSuperuserMixin,
                                 CSVResponseMixin, View):

    def get_self_registered_users(self):
        registered = RegistrationProfile.objects.values_list('user_id',
                                                             flat=True)
        return User.objects.filter(id__in=registered)

    def get_rows(self, users):
        rows = []
        for user in users:
            rows.append([user.first_name, user.last_name, user.email,
                        user.profile.title, user.profile.institution,
                        user.profile.referred_by, user.profile.user_story,
                        user.date_joined])
        return rows

    def get(self, request, *args, **kwargs):
        headers = ['First Name', 'Last Name', 'Email', 'Title',
                   'Institution', 'Referred_By', 'User Story',
                   'Created']

        users = self.get_self_registered_users()
        rows = self.get_rows(users)

        return self.render_csv_response(
            'mediathread_self_registration', headers, rows)


class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


class AssignmentDetailReport(LoggedInFacultyMixin, View):
    date_fmt = "%m/%d/%y %I:%M %p"

    def percent_used(self, selections, overall_count):
        try:
            return float(selections.count()) / overall_count * 100
        except ZeroDivisionError:
            return 0

    def tag_usage(self, selections):
        try:
            t = selections.filter(tags__isnull=False).exclude(tags__exact='')
            return float(t.count()) / selections.count() * 100
        except ZeroDivisionError:
            return 0

    def vocabulary_usage(self, selections):
        try:
            related = TermRelationship.objects.filter(
                sherdnote__id__in=selections.values_list('id', flat=True))
            return float(related.count()) / selections.count() * 100
        except ZeroDivisionError:
            return 0

    def citation_analysis(self, citations):
        ids = [c.id for c in citations]
        selections = SherdNote.objects.filter(id__in=ids).distinct()
        items = selections.get_related_assets()
        return items, selections

    def get_report_rows(self, responses):
        header = ['Student', 'Username', 'Title', 'Status',
                  'Initial Submit Date', 'Saved at', 'Faculty Feedback',
                  'Selections', 'Items',
                  'Author Selections', 'Author Items',
                  'Percent Author Selections Used',
                  'Tag Usage', 'Vocabulary Usage',
                  'All Author Selections', 'All Author Items']
        yield header

        for response in responses:
            dt = None
            if response.date_submitted:
                dt = response.date_submitted.strftime(self.date_fmt)

            row = [response.author.get_full_name(),
                   response.author.get_username(),
                   response.title, response.status(),
                   dt,
                   response.modified.strftime(self.date_fmt),
                   response.feedback_discussion() is not None]

            items, selections = self.citation_analysis(response.citations())

            # embedded citations - all
            row.append(selections.count())  # citation count
            row.append(items.count())  # citation parent item count. distinct.

            # embedded citations - response author only - a.k.a. "the subject"
            selections = selections.filter(author=response.author)
            items = selections.get_related_assets()
            row.append(selections.count())  # citation count
            row.append(items.count())  # citation parent item count. distinct.

            # *all* selections on "the subject" by response author
            all_count = SherdNote.objects.get_related_notes(
                items, response.author).count()

            row.append(self.percent_used(selections, all_count))
            row.append(self.tag_usage(selections))
            row.append(self.vocabulary_usage(selections))

            selections = SherdNote.objects.filter(author=response.author)
            row.append(selections.count())
            items = Asset.objects.by_course_and_user(self.request.course,
                                                     response.author)
            row.append(items.count())

            yield row

    def get(self, request, *args, **kwargs):
        assignment_id = kwargs.get('assignment_id', None)
        assignment = get_object_or_404(Project, id=assignment_id)
        responses = assignment.responses(request.course, request.user)

        rows = self.get_report_rows(responses)

        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)

        fnm = "%s.csv" % assignment.title
        response = StreamingHttpResponse(
            (writer.writerow(row) for row in rows), content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="' + fnm + '"'
        return response
