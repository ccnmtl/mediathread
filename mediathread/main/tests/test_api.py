# pylint: disable-msg=R0904
# pylint: disable-msg=E1103
from courseaffils.models import Course
from django.contrib.auth.models import User
from mediathread.api import UserResource
from tastypie.test import ResourceTestCase
from mediathread.factories import (UserFactory, GroupFactory, CourseFactory)


class UserApiTest(ResourceTestCase):

    def get_credentials(self):
        return None

    def test_render_one(self):
        u = UserFactory(username='test_student_one',
                        first_name='Student', last_name='One')
        self.assertTrue(
            self.api_client.client.login(username=u.username, password="test"))

        student_one = User.objects.get(username='test_student_one')

        member = UserResource().render_one(None, student_one)

        self.assertEquals(member['public_name'], "Student One")

    def test_render_list(self):
        u = UserFactory(username='test_student_one',
                        first_name='Student', last_name='One')

        self.assertTrue(
            self.api_client.client.login(username=u.username, password="test"))

        g1 = GroupFactory(name="group1")
        g2 = GroupFactory(name="group2")
        CourseFactory(title="Sample Course", faculty_group=g1, group=g2)
        u.groups.add(g2)
        UserFactory(username='instructor_one',
                    first_name='Instructor', last_name='One').groups.add(g2)
        UserFactory(username='test_instructor_two').groups.add(g2)
        UserFactory(username='test_student_three').groups.add(g2)
        UserFactory(username='student_two', first_name='Student',
                    last_name='Two').groups.add(g2)
        UserFactory(username='teachers_assistant',
                    first_name="Teacher's",
                    last_name=" Assistant").groups.add(g2)

        sample_course = Course.objects.get(title="Sample Course")

        members = UserResource().render_list(None, sample_course.members)

        self.assertEquals(len(members), 6)
        self.assertEquals(members[0]['public_name'], "test_instructor_two")
        self.assertEquals(members[1]['public_name'], "test_student_three")
        self.assertEquals(members[2]['public_name'], "Instructor One")
        self.assertEquals(members[3]['public_name'], "Student One")
        self.assertEquals(members[4]['public_name'], "Student Two")
        self.assertEquals(members[5]['public_name'], "Teacher's  Assistant")
