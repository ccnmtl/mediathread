#pylint: disable-msg=R0904
from courseaffils.models import Course
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.test import TestCase
from mediathread.assetmgr.models import Asset
from mediathread.djangosherd.models import SherdNote
from mediathread.projects.models import Project
from structuredcollaboration.models import Collaboration


class ProjectTest(TestCase):
    fixtures = ['unittest_sample_course.json',
                'unittest_sample_projects.json']

    def test_description(self):
        project = Project.objects.get(title='Private Composition')
        self.assertEquals(project.description(), 'Composition')
        self.assertEquals(project.visibility_short(), 'Private')

        project = Project.objects.get(title="Public To Class Composition")
        self.assertEquals(project.visibility_short(), 'Published to Class')

        project = Project.objects.get(title="Instructor Shared")
        self.assertEquals(project.visibility_short(),
                          'Submitted to Instructor')

        assignment = Project.objects.get(title='Sample Course Assignment')
        self.assertEquals(assignment.description(), 'Assignment')
        self.assertEquals(assignment.visibility_short(), 'Assignment')

    def test_verify_testdata(self):
        course = Course.objects.get(id=1)
        self.assertEquals(course.title, "Sample Course")

        alt_course = Course.objects.get(id=2)
        self.assertEquals(alt_course.title, "Alternate Course")

    def test_migrate_one(self):
        alt_course = Course.objects.get(id=2)
        self.assertEquals(alt_course.title, "Alternate Course")

        alt_instructor = User.objects.get(username='test_instructor_alt')

        private_essay = Project.objects.get(id=1)
        new_project = Project.objects.migrate_one(private_essay,
                                                  alt_course,
                                                  alt_instructor)

        self.assertEquals(new_project.title, "Private Composition")
        self.assertEquals(new_project.author, alt_instructor)
        self.assertEquals(new_project.course, alt_course)
        self.assertEquals(new_project.visibility_short(), "Private")

        assignment = Project.objects.get(id=5)
        new_project = Project.objects.migrate_one(assignment,
                                                  alt_course,
                                                  alt_instructor)

        self.assertEquals(new_project.title, "Sample Course Assignment")
        self.assertEquals(new_project.author, alt_instructor)
        self.assertEquals(new_project.course, alt_course)
        self.assertEquals(new_project.visibility_short(), "Assignment")

    def test_migrate_set(self):
        self.assertTrue(True)

        course = Course.objects.get(id=2)
        self.assertEquals(course.title, "Alternate Course")
        self.assertEquals(len(course.asset_set.all()), 1)
        self.assertEquals(len(course.project_set.all()), 2)

        user = User.objects.get(username='test_instructor_two')

        projects = Project.objects.filter(title="Sample Course Assignment")

        object_map = {'assets': {}, 'notes': {}, 'projects': {}}
        object_map = Project.objects.migrate(projects, course,
                                             user, object_map)

        self.assertEquals(len(course.asset_set.all()), 4)
        asset = Asset.objects.get(title="Mediathread: Introduction",
                                  course=course)
        self.assertEquals(len(asset.sherdnote_set.all()), 2)
        self.assertIsNotNone(asset.global_annotation(user, auto_create=False))
        asset.sherdnote_set.get(title="Video Selection Is Time-based")

        asset = Asset.objects.get(title="MAAP Award Reception",
                                  course=course)
        self.assertEquals(len(asset.sherdnote_set.all()), 2)
        self.assertIsNotNone(asset.global_annotation(user, auto_create=False))
        asset.sherdnote_set.get(title="Nice Tie")

        asset = Asset.objects.get(title="Project Portfolio",
                                  course=course)
        self.assertEquals(len(asset.sherdnote_set.all()), 1)

        self.assertEquals(len(course.project_set.all()), 3)
        assignment = Project.objects.get(title="Sample Course Assignment",
                                         course=course)
        self.assertEquals(assignment.visibility_short(), 'Assignment')
        self.assertEquals(assignment.author, user)

        citations = SherdNote.objects.references_in_string(assignment.body,
                                                           user)
        self.assertEquals(len(citations), 5)

        # Student annotation
        self.assertEquals(citations[0].title, "Nice Tie")
        self.assertEquals(citations[0].range1, 0.0)
        self.assertEquals(citations[0].range2, 0.0)
        annotation_data = ('{"geometry":{"type":"Polygon",'
                           '"coordinates":[[[38.5,-91],[38.5,2.5],[61.5,'
                           '2.500000000000007],[61.5,-91],[38.5,-91]]]},'
                           '"default":false,"x":0,"y":0,"zoom":2,'
                           '"extent":[-120,-90,120,90]}')
        self.assertEquals(citations[0].annotation_data, annotation_data)
        self.assertEquals(citations[0].tags, ',student_two_selection')
        self.assertEquals(citations[0].body, 'student two selection note')
        self.assertEquals(citations[0].author, user)

        # Migrated global annotation
        self.assertTrue(citations[1].asset.title,
                        "Mediathread: Introduction")
        self.assertEquals(citations[1].id,
                          citations[1].asset.global_annotation(user, False).id)
        self.assertEquals(citations[1].tags, ',test_instructor_two')
        self.assertEquals(citations[1].body, 'test_instructor_two notes')

        # Own selection
        self.assertEquals(citations[2].title, "Video Selection Is Time-based")
        self.assertEquals(citations[2].range1, 60.0)
        self.assertEquals(citations[2].range2, 120.0)
        annotation_data = ('{"startCode":"00:01:00","endCode":"00:02:00",'
                           '"duration":171,"timeScale":1,"start":60,'
                           '"end":120}')
        self.assertEquals(citations[2].annotation_data, annotation_data)
        self.assertEquals(citations[2].tags, ',test_instructor_two')
        self.assertEquals(citations[2].author, user)

        # Own asset
        self.assertTrue(citations[3].asset.title, "Project Portfolio")
        self.assertTrue(citations[3].is_global_annotation())
        self.assertEquals(citations[3].id,
                          citations[3].asset.global_annotation(user, False).id)

        # Own global annotation
        self.assertTrue(citations[4].asset.title,
                        "Mediathread: Introduction")
        self.assertEquals(citations[4].id,
                          citations[4].asset.global_annotation(user, False).id)

    def test_visible_by_course(self):
        student_one = User.objects.get(username='test_student_one')
        student_two = User.objects.get(username='test_student_two')
        instructor = User.objects.get(username='test_instructor')

        sample_course = Course.objects.get(title="Sample Course")

        request = HttpRequest()
        request.course = sample_course
        request.collaboration_context, created = \
            Collaboration.objects.get_or_create(
                content_type=ContentType.objects.get_for_model(Course),
                object_pk=str(sample_course.pk))

        request.user = student_one
        visible_projects = Project.objects.visible_by_course(request,
                                                             sample_course)
        self.assertEquals(len(visible_projects), 4)
        self.assertEquals(visible_projects[0].__unicode__(),
                          "Sample Course Assignment <5> "
                          "by test_instructor_two")
        self.assertEquals(visible_projects[1].__unicode__(),
                          "Public To Class Composition <3> by Student One")
        self.assertEquals(visible_projects[2].__unicode__(),
                          "Instructor Shared <2> by Student One")
        self.assertEquals(visible_projects[3].__unicode__(),
                          "Private Composition <1> by Student One")

        request.user = student_two
        visible_projects = Project.objects.visible_by_course(request,
                                                             sample_course)
        self.assertEquals(len(visible_projects), 2)
        self.assertEquals(visible_projects[0].__unicode__(),
                          "Sample Course Assignment <5> "
                          "by test_instructor_two")
        self.assertEquals(visible_projects[1].__unicode__(),
                          "Public To Class Composition <3> by Student One")

        request.user = instructor
        visible_projects = Project.objects.visible_by_course(request,
                                                             sample_course)
        self.assertEquals(len(visible_projects), 3)
        self.assertEquals(visible_projects[0].__unicode__(),
                          "Sample Course Assignment <5> "
                          "by test_instructor_two")
        self.assertEquals(visible_projects[1].__unicode__(),
                          "Public To Class Composition <3> by Student One")
        self.assertEquals(visible_projects[2].__unicode__(),
                          "Instructor Shared <2> by Student One")

    def test_visible_by_course_and_user(self):
        student_one = User.objects.get(username='test_student_one')
        student_two = User.objects.get(username='test_student_two')
        instructor = User.objects.get(username='test_instructor_two')

        sample_course = Course.objects.get(title="Sample Course")

        request = HttpRequest()
        request.course = sample_course
        request.collaboration_context, created = \
            Collaboration.objects.get_or_create(
                content_type=ContentType.objects.get_for_model(Course),
                object_pk=str(sample_course.pk))

        request.user = student_one
        visible_projects = Project.objects.visible_by_course_and_user(
            request, sample_course, student_one)
        self.assertEquals(len(visible_projects), 3)
        self.assertEquals(visible_projects[0].__unicode__(),
                          "Public To Class Composition <3> by Student One")
        self.assertEquals(visible_projects[1].__unicode__(),
                          "Instructor Shared <2> by Student One")
        self.assertEquals(visible_projects[2].__unicode__(),
                          "Private Composition <1> by Student One")

        visible_projects = Project.objects.visible_by_course_and_user(
            request, sample_course, instructor)
        self.assertEquals(len(visible_projects), 1)
        self.assertEquals(visible_projects[0].__unicode__(),
                          "Sample Course Assignment <5> "
                          "by test_instructor_two")

        request.user = student_two
        visible_projects = Project.objects.visible_by_course_and_user(
            request, sample_course, student_one)
        self.assertEquals(len(visible_projects), 1)
        self.assertEquals(visible_projects[0].__unicode__(),
                          "Public To Class Composition <3> by Student One")

        request.user = instructor
        visible_projects = Project.objects.visible_by_course_and_user(
            request, sample_course, student_one)
        self.assertEquals(len(visible_projects), 2)
        self.assertEquals(visible_projects[0].__unicode__(),
                          "Public To Class Composition <3> by Student One")
        self.assertEquals(visible_projects[1].__unicode__(),
                          "Instructor Shared <2> by Student One")

    def test_project_clean(self):
        assignment = Project.objects.get(id=5)
        try:
            assignment.due_date = datetime(2012, 3, 13, 0, 0)
            assignment.clean()
            self.assertTrue(False, 'Due date is in the past')
        except ValidationError as err:
            self.assertTrue(
                err.messages[0].startswith('03/13/12 is not valid'))

        try:
            today = datetime.today()
            this_day = datetime(today.year, today.month, today.day, 0, 0)
            assignment.due_date = this_day
            assignment.clean()
        except ValidationError as err:
            self.assertTrue(False, "Due date is today. That's okay.")

        try:
            assignment.due_date = datetime(2020, 1, 1, 0, 0)
            assignment.clean()
        except ValidationError as err:
            self.assertTrue(False, "Due date is in the future, that's ok")

    def test_faculty_compositions(self):
        student = User.objects.get(username='test_student_three')
        sample_course = Course.objects.get(title="Sample Course")
        alt_course = Course.objects.get(title="Alternate Course")

        request = HttpRequest()
        request.user = student
        request.course = sample_course
        request.collaboration_context, created = \
            Collaboration.objects.get_or_create(
                content_type=ContentType.objects.get_for_model(Course),
                object_pk=str(sample_course.pk))

        compositions = Project.objects.faculty_compositions(
            request, sample_course)
        self.assertEquals(len(compositions), 0)

        request.course = alt_course
        request.collaboration_context, created = \
            Collaboration.objects.get_or_create(
                content_type=ContentType.objects.get_for_model(Course),
                object_pk=str(alt_course.pk))

        compositions = Project.objects.faculty_compositions(
            request, alt_course)
        self.assertEquals(len(compositions), 1)
