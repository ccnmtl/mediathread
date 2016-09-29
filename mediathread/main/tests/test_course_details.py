from django.test.testcases import TestCase

from mediathread.factories import MediathreadTestMixin, UserFactory
from mediathread.main.course_details import can_upload, \
    UPLOAD_PERMISSION_KEY, UPLOAD_PERMISSION_ADMINISTRATOR, \
    UPLOAD_PERMISSION_STUDENT, \
    allow_public_compositions, all_selections_are_visible, \
    all_items_are_visible, \
    course_information_title, COURSE_INFORMATION_TITLE_DEFAULT, \
    cached_course_is_member, cached_course_is_faculty, is_upload_enabled, \
    allow_item_download


class TestCourseDetails(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.superuser = UserFactory(is_superuser=True, is_staff=True)

    def test_can_upload(self):
        # default value - instructor level
        self.assertTrue(can_upload(self.superuser, self.sample_course))
        self.assertTrue(can_upload(self.instructor_one, self.sample_course))
        self.assertFalse(can_upload(self.student_one, self.sample_course))

        # set to - administrators only
        self.sample_course.add_detail(UPLOAD_PERMISSION_KEY,
                                      UPLOAD_PERMISSION_ADMINISTRATOR)
        self.assertTrue(can_upload(self.superuser, self.sample_course))
        self.assertFalse(can_upload(self.instructor_one, self.sample_course))
        self.assertFalse(can_upload(self.student_one, self.sample_course))

        # set to - student, instructor & admins
        self.sample_course.add_detail(UPLOAD_PERMISSION_KEY,
                                      UPLOAD_PERMISSION_STUDENT)
        self.assertTrue(can_upload(self.superuser, self.sample_course))
        self.assertTrue(can_upload(self.instructor_one, self.sample_course))
        self.assertTrue(can_upload(self.student_one, self.sample_course))

    def test_allow_public_compositions(self):
        # default
        self.assertFalse(allow_public_compositions(self.sample_course))

    def test_all_selections_are_visible(self):
        # default
        self.assertTrue(all_selections_are_visible(self.sample_course))

    def all_items_are_visible(self):
        # default
        self.assertFalse(all_items_are_visible(self.sample_course))

    def allow_item_download(self):
        # default
        self.assertFalse(allow_item_download(self.sample_course))

    def test_course_information_title(self):
        # default
        self.assertEquals(course_information_title(self.sample_course),
                          COURSE_INFORMATION_TITLE_DEFAULT)

    def test_cached_course_is_member(self):
        self.assertTrue(cached_course_is_member(self.sample_course,
                                                self.student_one))
        self.assertTrue(cached_course_is_member(self.sample_course,
                                                self.student_one))

    def test_cached_course_is_faculty(self):
        self.assertTrue(cached_course_is_faculty(self.sample_course,
                                                 self.instructor_one))
        self.assertTrue(cached_course_is_faculty(self.sample_course,
                                                 self.instructor_one))

    def test_is_upload_enabled(self):
        self.assertFalse(is_upload_enabled(self.sample_course))
        self.enable_upload(self.sample_course)
        self.assertTrue(is_upload_enabled(self.sample_course))
