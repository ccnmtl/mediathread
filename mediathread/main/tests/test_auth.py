from django.test.testcases import TestCase

from mediathread.factories import UserFactory, CourseFactory
from mediathread.main.auth import CourseGroupMapper


class TestCourseGroupMapper(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.course = CourseFactory()

    def test_map_user_uniremoved(self):
        affils = [self.user.username]
        self.assertEquals(self.user.groups.count(), 0)

        CourseGroupMapper().map(self.user, affils)
        self.assertEquals(self.user.groups.count(), 0)

    def test_map_user_group_does_not_exist(self):
        affils = [self.user.username,
                  'CUcourse_ENGLW3872:columbia.edu']
        self.assertEquals(self.user.groups.count(), 0)

        CourseGroupMapper().map(self.user, affils)
        self.assertEquals(self.user.groups.count(), 0)

    def test_map_user_student_affiliation(self):
        affils = [self.user.username, self.course.group.name]
        self.assertEquals(self.user.groups.count(), 0)

        CourseGroupMapper().map(self.user, affils)
        self.assertEquals(self.user.groups.count(), 1)
        self.assertTrue(self.course.group in self.user.groups.all())

    def test_map_user_faculty_affiliation(self):
        affils = [self.user.username,
                  self.course.group.name,
                  self.course.faculty_group.name]

        self.assertEquals(self.user.groups.count(), 0)

        CourseGroupMapper().map(self.user, affils)
        self.assertEquals(self.user.groups.count(), 2)
        self.assertTrue(self.course.group in self.user.groups.all())
        self.assertTrue(self.course.faculty_group in self.user.groups.all())
