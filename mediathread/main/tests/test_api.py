#pylint: disable-msg=R0904
#pylint: disable-msg=E1103
from courseaffils.models import Course
from django.contrib.auth.models import User
from mediathread.api import UserResource
from tastypie.test import ResourceTestCase


class UserApiTest(ResourceTestCase):
    # Use ``fixtures`` & ``urls`` as normal. See Django's ``TestCase``
    # documentation for the gory details.
    fixtures = ['unittest_sample_course.json']

    def get_credentials(self):
        return None

    def test_render_one(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        student_one = User.objects.get(username='test_student_one')

        member = UserResource().render_one(None, student_one)

        self.assertEquals(member['public_name'], "Student One")

    def test_render_list(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        sample_course = Course.objects.get(title="Sample Course")

        members = UserResource().render_list(None, sample_course.members)

        self.assertEquals(len(members), 6)
        self.assertEquals(members[0]['public_name'], "test_instructor_two")
        self.assertEquals(members[1]['public_name'], "test_student_three")
        self.assertEquals(members[2]['public_name'], "Instructor One")
        self.assertEquals(members[3]['public_name'], "Student One")
        self.assertEquals(members[4]['public_name'], "Student Two")
        self.assertEquals(members[5]['public_name'], "Teacher's  Assistant")
