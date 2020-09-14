from datetime import datetime, timedelta

from courseaffils.models import Course
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test.client import RequestFactory
from django.urls import reverse
from django.utils.text import slugify
import factory
from factory.django import DjangoModelFactory
import json
from mediathread.assetmgr.models import (
    Asset, Source, ExternalCollection,
    SuggestedExternalCollection,
)
from mediathread.djangosherd.models import SherdNote
from mediathread.discussions.views import DiscussionCreateView
from mediathread.main.models import UserProfile, CourseInvitation
from mediathread.projects.models import Project, AssignmentItem, ProjectNote
from mediathread.taxonomy.models import Vocabulary, Term, TermRelationship
from registration.models import RegistrationProfile
from structuredcollaboration.models import Collaboration, \
    CollaborationPolicyRecord
from threadedcomments.models import ThreadedComment


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    is_staff = False
    username = factory.Sequence(lambda n: 'user%d' % n)
    password = factory.PostGenerationMethodCall('set_password', 'test')
    email = factory.LazyAttribute(lambda u: '%s@example.com' % u.username)


class UserProfileFactory(DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(UserFactory)
    title = 'Title'
    institution = 'Columbia University'
    referred_by = 'Pablo Picasso'
    user_story = 'User Story'
    self_registered = True


class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group
    name = factory.Sequence(
        lambda n: 't1.y2010.s001.cf1000.scnc.st.course:%d.columbia.edu' % n)


class RegistrationProfileFactory(DjangoModelFactory):
    class Meta:
        model = RegistrationProfile
    user = factory.SubFactory(UserFactory)
    activation_key = factory.Sequence(lambda n: 'key%d' % n)


class CourseFactory(DjangoModelFactory):
    class Meta:
        model = Course
    title = 'Sample Course'
    faculty_group = factory.SubFactory(GroupFactory)
    group = factory.SubFactory(GroupFactory)

    @factory.post_generation
    def create_collaboration(self, create, extracted, **kwargs):
        if create:
            coll, created = Collaboration.objects.get_or_create(
                content_type=ContentType.objects.get_for_model(Course),
                object_pk=self.pk, slug=slugify(self.title))

            coll.slug = self.slug()
            coll.title = self.title
            coll.group = self.group
            coll.save()


class SourceFactory(DjangoModelFactory):
    class Meta:
        model = Source

    asset = factory.SubFactory('mediathread.factories.AssetFactory')
    label = 'image'
    url = 'sample url'
    media_type = 'ext'


class AssetFactory(DjangoModelFactory):
    class Meta:
        model = Asset
    title = factory.Sequence(lambda n: 'asset %d' % n)
    author = factory.SubFactory(UserFactory)
    course = factory.SubFactory(CourseFactory)

    @factory.post_generation
    def primary_source(self, create, extracted, **kwargs):
        if create and extracted:
            # A list of groups were passed in, use them
            source = SourceFactory(
                primary=True, label=extracted, url='source url', asset=self)
            self.source_set.add(source)


class ExternalCollectionFactory(DjangoModelFactory):
    class Meta:
        model = ExternalCollection

    title = 'collection'
    url = 'http://ccnmtl.columbia.edu'
    description = 'description'
    course = factory.SubFactory(CourseFactory)


class SuggestedExternalCollectionFactory(DjangoModelFactory):
    class Meta:
        model = SuggestedExternalCollection

    title = 'collection'
    url = 'http://ccnmtl.columbia.edu'
    description = 'description'


class SherdNoteFactory(DjangoModelFactory):
    class Meta:
        model = SherdNote
    title = factory.Sequence(lambda n: 'note %d' % n)
    range1 = 0.0
    range2 = 0.0
    asset = factory.SubFactory(AssetFactory, primary_source='image')
    author = factory.SubFactory(UserFactory)


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project
    course = factory.SubFactory(CourseFactory)
    title = factory.Sequence(lambda n: 'Project %d' % n)
    author = factory.SubFactory(UserFactory)
    project_type = 'composition'

    @factory.post_generation
    def policy(self, create, extracted, **kwargs):
        if create:
            data = {'publish': 'PrivateEditorsAreOwners'}
            if extracted:
                data = {'publish': extracted}

            self.create_or_update_collaboration(data['publish'])

    @factory.post_generation
    def parent(self, create, extracted, **kwargs):
        if create and extracted:
            self.set_parent(extracted.id)

    @factory.post_generation
    def participants(self, create, extracted, **kwargs):
        if create:
            self.participants.add(self.author)


class CollaborationFactory(DjangoModelFactory):
    class Meta:
        model = Collaboration
    user = factory.SubFactory(UserFactory)
    group = factory.SubFactory(GroupFactory)


class CollaborationPolicyRecordFactory(DjangoModelFactory):
    class Meta:
        model = CollaborationPolicyRecord


class AssignmentItemFactory(DjangoModelFactory):
    class Meta:
        model = AssignmentItem


class ProjectNoteFactory(DjangoModelFactory):
    class Meta:
        model = ProjectNote

    project = factory.SubFactory(ProjectFactory)


class CourseInvitationFactory(DjangoModelFactory):
    class Meta:
        model = CourseInvitation

    email = factory.Sequence(lambda n: '%s@example.com' % n)


class MediathreadTestMixin(object):

    def create_discussion(self, course, instructor):
        data = {
            'comment_html': '%s Discussion' % course.title,
            'obj_pk': course.id,
            'model': 'course',
            'app_label': 'courseaffils'
        }
        request = RequestFactory().post(
            reverse('discussion-create', args=[course.pk]),
            data,
            # Mock an ajax request because the response is simpler to
            # deal with manually here.
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = instructor
        request.course = course
        request.collaboration_context, created = \
            Collaboration.objects.get_or_create(
                content_type=ContentType.objects.get_for_model(Course),
                object_pk=course.pk)
        view = DiscussionCreateView()
        view.request = request
        response = view.post(request)

        response_data = json.loads(response.content)
        thread_id = response_data.get('context').get('discussion').get('id')

        return ThreadedComment.objects.get(id=thread_id)

    def add_comment(self, parent_comment, author):
        comment = ThreadedComment.objects.create(
            site=Site.objects.all().first(),
            content_type=ContentType.objects.get_for_model(ThreadedComment),
            parent=parent_comment, comment='test comment',
            user=author)
        return comment

    def create_vocabularies(self, course, taxonomy):
        for name, terms in taxonomy.items():
            concept = Vocabulary(display_name=name, course=course)
            concept.save()
            for term_name in terms:
                term = Term(display_name=term_name, vocabulary=concept)
                term.save()

    def create_term_relationship(self, note, term):
        # Add some tags to a few notes
        TermRelationship.objects.get_or_create(term=term, sherdnote=note)

    def add_citation(self, project, note):
        # add this note into the project's body
        fmt = '%s <a class="materialCitation" href="/%s/%s/%s/%s/">%s</a>'
        project.body = fmt % (project.body,
                              'asset', note.asset.id,
                              'annotations', note.id, note.title)
        project.save()

    def add_as_student(self, course, user):
        user.groups.add(course.group)

    def add_as_faculty(self, course, user):
        user.groups.add(course.group)
        user.groups.add(course.faculty_group)

    def setup_sample_course(self):
        self.instructor_one = UserFactory(
            username='instructor_one', email='instructor_one@example.com',
            first_name='Instructor', last_name='One')
        self.instructor_two = UserFactory(
            username='instructor_two', email='instructor_two@example.com',
            first_name='Instructor', last_name='Two')
        self.student_one = UserFactory(
            username='student_one', email='student_one@example.com',
            first_name='Student', last_name='One')
        self.student_two = UserFactory(
            username='student_two', email='student_two@example.com',
            first_name='Student', last_name='Two')
        self.student_three = UserFactory(
            username='student_three', email='student_three@example.com',
            first_name='Student', last_name='Three')

        self.superuser = UserFactory(
            username='superuser', is_staff=True, is_superuser=True)

        self.sample_course = CourseFactory(title='Sample Course')

        self.add_as_student(self.sample_course, self.student_one)
        self.add_as_student(self.sample_course, self.student_two)
        self.add_as_student(self.sample_course, self.student_three)

        self.add_as_faculty(self.sample_course, self.instructor_one)
        self.add_as_faculty(self.sample_course, self.instructor_two)

    def setup_alternate_course(self):
        self.alt_instructor = UserFactory(
            username='alt_instructor', email='alt_instructor@example.com',
            first_name='Instructor', last_name='Alternate')
        self.alt_student = UserFactory(
            username='alt_student', email='alt_student@example.com',
            first_name='Student', last_name='Alternate')

        self.alt_course = CourseFactory(title='Alternate Course')

        self.add_as_student(self.alt_course, self.alt_student)
        self.add_as_faculty(self.alt_course, self.alt_instructor)

        # add student three from sample course
        self.add_as_student(self.alt_course, self.student_three)

    def switch_course(self, client, course):
        # assumes there is a logged in user
        return client.get(reverse('course_detail', args=[course.id]))

    def enable_upload(self, course):
        ExternalCollectionFactory.create(course=course,
                                         uploader=True)

    def setup_teaching_assistant(self):
        ct = ContentType.objects.get_for_model(Asset)
        permission, created = Permission.objects.get_or_create(
            content_type=ct, codename='can_upload_for')

        ta = UserFactory(username='teaching_assistant')
        ta.user_permissions.add(permission)
        self.add_as_student(self.sample_course, ta)

    def setup_suggested_collection(self):
        SuggestedExternalCollectionFactory(title='YouTube',
                                           url='https://www.youtube.com')

    def setup_sample_assignment(self):
        assignment = ProjectFactory.create(
            title='Sample Assignment',
            course=self.sample_course, author=self.instructor_one,
            policy='CourseProtected', project_type='assignment')
        return assignment

    def setup_sample_assignment_and_response(self):
        assignment = self.setup_sample_assignment()
        ProjectFactory.create(
            title='Sample Assignment Response', course=self.sample_course,
            author=self.student_one, policy='InstructorShared',
            project_type='composition', parent=assignment,
            response_view_policy='always', date_submitted=datetime.now(),
            body='Sample assignment response text')

    def setup_sample_selection_assignment(self):
        assignment = ProjectFactory.create(
            title='Sample Selection Assignment',
            course=self.sample_course, author=self.instructor_one,
            policy='CourseProtected', project_type='selection-assignment',
            due_date=datetime.today() + timedelta(1))

        item = AssetFactory.create(
                title='Selection Assignment Item', primary_source='image',
                author=self.instructor_one, course=self.sample_course)
        AssignmentItemFactory(project=assignment, asset=item)

        return assignment

    def setup_sample_selection_assignment_and_response(self):
        assignment = self.setup_sample_selection_assignment()
        ai = assignment.assignmentitem_set.first()

        response = ProjectFactory.create(
            title='My Response', course=self.sample_course,
            author=self.student_one, policy='InstructorShared',
            project_type='composition', parent=assignment,
            response_view_policy='always', date_submitted=datetime.now())

        note = SherdNoteFactory.create(
            asset=ai.asset, author=self.student_one, range1=0, range2=1)
        ProjectNoteFactory(project=response, annotation=note)

    def setup_sample_assets(self):
        items = [
            AssetFactory(
                title='MAAP Award Reception', primary_source='image',
                author=self.instructor_one, course=self.sample_course),
            AssetFactory(
                title='Mediathread: Introduction', primary_source='image',
                author=self.instructor_one, course=self.sample_course),
            AssetFactory(
                title='The Armory - Home to CCNMTL\'s CUMC Office',
                primary_source='image',
                author=self.instructor_one, course=self.sample_course),
        ]

        for idx, item in enumerate(items):
            if idx == 0:  # everyone has the first item
                a = [self.instructor_one, self.student_one, self.student_two]
            else:  # the instructor has all the items
                a = [self.instructor_one]

            for user in a:
                SherdNoteFactory(asset=item, author=user,
                                 tags=',{}_item'.format(user.username),
                                 body='{} item note'.format(user.username),
                                 title=None, range1=None, range2=None)

        # instructor one selections
        SherdNoteFactory(
            title='Our esteemed leaders',
            asset=items[0], author=self.instructor_one,
            body='instructor one selection note',
            tags=',instructor_one_selection,flickr', range1=0, range2=1)
        SherdNoteFactory(
            title='Manage Sources',
            asset=items[1], author=self.instructor_one,
            tags=',instructor_one_selection,video', range1=0, range2=1)
        SherdNoteFactory(
            title='Left Corner',
            asset=items[2], author=self.instructor_one,
            tags=',instructor_one_selection,flickr', range1=0, range2=1)

        # student one selections
        SherdNoteFactory(
            title='The Award',
            asset=items[0], author=self.student_one,
            body='student one selection note',
            tags=',student_one_selection', range1=0, range2=1)

        # student two selections
        SherdNoteFactory(
            title='Nice Tie',
            asset=items[0], author=self.student_two,
            body='student two selection note',
            tags=',student_two_selection', range1=0, range2=1)


class LoggedInStaffTestMixin(object):
    def setUp(self):
        self.u = UserFactory(username='test_user', is_staff=True)
        self.u.set_password('test')
        self.u.save()
        login = self.client.login(username='test_user',
                                  password='test')
        assert(login is True)
