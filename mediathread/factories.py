from courseaffils.models import Course
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.test.testcases import TestCase
import factory

from mediathread.assetmgr.models import Asset
from mediathread.djangosherd.models import SherdNote
from mediathread.taxonomy.models import Vocabulary, Term, TermRelationship


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: 'user%d' % n)
    password = 'test'


class GroupFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Group
    name = factory.Sequence(lambda n: 'group %d' % n)


class CourseFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Course
    title = "Sample Course"
    faculty_group = factory.SubFactory(GroupFactory)
    group = factory.SubFactory(GroupFactory)


class AssetFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Asset
    title = factory.Sequence(lambda n: 'asset %d' % n)
    author = factory.SubFactory(UserFactory)
    course = factory.SubFactory(CourseFactory)


class SherdNoteFactory(factory.DjangoModelFactory):
    FACTORY_FOR = SherdNote
    title = factory.Sequence(lambda n: 'note %d' % n)
    range1 = 0.0
    range2 = 0.0
    asset = factory.SubFactory(AssetFactory)
    author = factory.SubFactory(UserFactory)


class MediathreadTestCase(TestCase):

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

    def setUp(self):
        self.instructor_one = UserFactory(username='instructor_one',
                                          first_name='Instructor',
                                          last_name='One')
        self.instructor_two = UserFactory(username='test_instructor_two')

        self.student_one = UserFactory(username='student_one',
                                       first_name='Student',
                                       last_name='One')
        self.student_two = UserFactory(username='student_two',
                                       first_name='Student',
                                       last_name='Two')
        self.student_three = UserFactory(username='test_student_three')
        self.ta = UserFactory(username='teachers_assistant',
                              first_name="Teacher's",
                              last_name=" Assistant")

        self.sample_course = CourseFactory(title="Sample Course")
        self.instructor_one.groups.add(self.sample_course.group)
        self.instructor_two.groups.add(self.sample_course.group)
        self.student_one.groups.add(self.sample_course.group)
        self.student_two.groups.add(self.sample_course.group)
        self.student_three.groups.add(self.sample_course.group)

        self.instructor_one.groups.add(self.sample_course.faculty_group)
        self.instructor_two.groups.add(self.sample_course.faculty_group)
