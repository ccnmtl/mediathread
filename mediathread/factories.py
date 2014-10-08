from courseaffils.models import Course
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.test.client import RequestFactory
import factory

from mediathread.assetmgr.models import Asset, Source
from mediathread.djangosherd.models import SherdNote
from mediathread.projects.models import Project
from mediathread.taxonomy.models import Vocabulary, Term, TermRelationship
from structuredcollaboration.models import Collaboration


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: 'user%d' % n)
    password = factory.PostGenerationMethodCall('set_password', 'test')


class GroupFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Group
    name = factory.Sequence(lambda n: 'group%d' % n)


class CourseFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Course
    title = "Sample Course"
    faculty_group = factory.SubFactory(GroupFactory)
    group = factory.SubFactory(GroupFactory)

    @factory.post_generation
    def create_collaboration(self, create, extracted, **kwargs):
        if create:
            Collaboration.objects.get_or_create(
                content_type=ContentType.objects.get_for_model(Course),
                object_pk=str(self.pk))


class SourceFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Source
    url = 'sample url'
    media_type = 'ext'


class AssetFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Asset
    title = factory.Sequence(lambda n: 'asset %d' % n)
    author = factory.SubFactory(UserFactory)
    course = factory.SubFactory(CourseFactory)

    @factory.post_generation
    def primary_source(self, create, extracted, **kwargs):
        if create and extracted:
            # A list of groups were passed in, use them
            source = SourceFactory(primary=True,
                                   label=extracted,
                                   asset=self)
            self.source_set.add(source)


class SherdNoteFactory(factory.DjangoModelFactory):
    FACTORY_FOR = SherdNote
    title = factory.Sequence(lambda n: 'note %d' % n)
    range1 = 0.0
    range2 = 0.0
    asset = factory.SubFactory(AssetFactory)
    author = factory.SubFactory(UserFactory)


class ProjectFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Project
    course = factory.SubFactory(CourseFactory)
    title = factory.Sequence(lambda n: 'Project %d' % n)
    author = factory.SubFactory(UserFactory)

    @factory.post_generation
    def policy(self, create, extracted, **kwargs):
        if create:
            data = {'publish': 'PrivateEditorsAreOwners'}
            if extracted:
                data = {'publish': extracted}

            request = RequestFactory().post('/', data)
            request.collaboration_context = \
                Collaboration.objects.get(
                    content_type=ContentType.objects.get_for_model(Course),
                    object_pk=str(self.course.pk))

            self.collaboration(request, sync_group=True)


class MediathreadTestMixin(object):

    def create_vocabularies(self, course, taxonomy):
        course_type = ContentType.objects.get_for_model(course)

        for name, terms in taxonomy.items():
            concept = Vocabulary(display_name=name,
                                 content_type=course_type,
                                 object_id=course.id)
            concept.save()
            for term_name in terms:
                term = Term(display_name=term_name,
                            vocabulary=concept)
                term.save()

    def create_term_relationship(self, content_object, term):
        # Add some tags to a few notes
        content_type = ContentType.objects.get_for_model(content_object)
        TermRelationship.objects.get_or_create(
            term=term,
            content_type=content_type,
            object_id=content_object.id)

    def add_citation(self, project, note):
        # add this note into the project's body
        project.body = '''%s <a class="materialCitation asset-image"
            href="/asset/%s/annotations/%s/"   ''' % (project.body,
                                                      note.asset.id,
                                                      note.id)
        project.save()

    def add_as_student(self, course, user):
        user.groups.add(course.group)

    def add_as_faculty(self, course, user):
        user.groups.add(course.group)
        user.groups.add(course.faculty_group)

    def setup_sample_course(self):
        self.instructor_one = UserFactory(username='instructor_one')
        self.instructor_two = UserFactory(username='instructor_two')

        self.student_one = UserFactory(username='student_one')
        self.student_two = UserFactory(username='student_two')
        self.student_three = UserFactory(username='student_three')

        self.sample_course = CourseFactory(title="Sample Course")

        self.add_as_student(self.sample_course, self.student_one)
        self.add_as_student(self.sample_course, self.student_two)
        self.add_as_student(self.sample_course, self.student_three)

        self.add_as_faculty(self.sample_course, self.instructor_one)
        self.add_as_faculty(self.sample_course, self.instructor_two)

    def setup_alternate_course(self):
        self.alt_instructor = UserFactory(username='alt_instructor',
                                          first_name='Instructor',
                                          last_name='Alternate')
        self.alt_student = UserFactory(username='alt_student',
                                       first_name='Student',
                                       last_name='Alternate')

        self.alt_course = CourseFactory(title="Alternate Course")

        self.add_as_student(self.alt_course, self.alt_student)
        self.add_as_faculty(self.alt_course, self.alt_instructor)
