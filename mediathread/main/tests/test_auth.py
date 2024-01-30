from django.test import TestCase, override_settings
from django.contrib.auth.models import AnonymousUser
from courseaffils.columbia import CourseStringMapper

from mediathread.factories import UserFactory, CourseFactory
from mediathread.main.auth import CourseGroupMapper


@override_settings(COURSEAFFILS_COURSESTRING_MAPPER=CourseStringMapper)
class TestCourseGroupMapper(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.course = CourseFactory()

    def test_map_user_uniremoved(self):
        affils = [self.user.username]
        self.assertEqual(self.user.groups.count(), 0)

        CourseGroupMapper.map(self.user, affils)
        self.assertEqual(self.user.groups.count(), 0)

    def test_map_user_group_does_not_exist(self):
        affils = [self.user.username,
                  'CUcourse_ENGLW3872:columbia.edu']
        self.assertEqual(self.user.groups.count(), 0)

        CourseGroupMapper.map(self.user, affils)
        self.assertEqual(self.user.groups.count(), 0)

    def test_map_user_student_affiliation(self):
        affils = [self.user.username, self.course.group.name]
        self.assertEqual(self.user.groups.count(), 0)

        CourseGroupMapper.map(self.user, affils)
        self.assertEqual(self.user.groups.count(), 1)
        self.assertTrue(self.course.group in self.user.groups.all())

    def test_map_user_faculty_affiliation(self):
        affils = [self.user.username,
                  self.course.group.name,
                  self.course.faculty_group.name]

        self.assertEqual(self.user.groups.count(), 0)

        CourseGroupMapper.map(self.user, affils)
        self.assertEqual(self.user.groups.count(), 2)
        self.assertTrue(self.course.group in self.user.groups.all())
        self.assertTrue(self.course.faculty_group in self.user.groups.all())

    def test_create_activatable_affil_empty_course_string(self):
        self.assertIsNone(
            CourseGroupMapper.create_activatable_affil(self.user, '', 2016))
        self.assertIsNone(
            CourseGroupMapper.create_activatable_affil(self.user, '', None))
        self.assertIsNone(
            CourseGroupMapper.create_activatable_affil(None, '', None))
        self.assertIsNone(
            CourseGroupMapper.create_activatable_affil(
                AnonymousUser(), '', 2016))

    def test_create_activatable_affil_student_course_string(self):
        s = 't1.y2016.s001.cf1000.scnc.st.course:columbia.edu'
        self.assertIsNone(
            CourseGroupMapper.create_activatable_affil(self.user, s, 2016))
        self.assertIsNone(
            CourseGroupMapper.create_activatable_affil(self.user, s, None))
        self.assertIsNone(
            CourseGroupMapper.create_activatable_affil(None, s, None))
        self.assertIsNone(
            CourseGroupMapper.create_activatable_affil(
                AnonymousUser(), s, 2016))

    def test_create_activatable_affil_faculty_course_string(self):
        s = 't1.y2016.s001.cf1000.scnc.fc.course:columbia.edu'
        aa = CourseGroupMapper.create_activatable_affil(self.user, s, 2016)
        self.assertIsNotNone(aa)
        self.assertEqual(aa.name, s)
        self.assertEqual(aa.user, self.user)

        self.assertIsNone(
            CourseGroupMapper.create_activatable_affil(self.user, s, 2017))
        self.assertIsNone(
            CourseGroupMapper.create_activatable_affil(self.user, s, None))
        self.assertIsNone(
            CourseGroupMapper.create_activatable_affil(None, s, None))
        self.assertIsNone(
            CourseGroupMapper.create_activatable_affil(
                AnonymousUser(), s, 2016))

    def test_create_activatable_affil_misc_course_string(self):
        self.assertIsNone(
            CourseGroupMapper.create_activatable_affil(
                self.user, 'ALL_CU', 2016))
