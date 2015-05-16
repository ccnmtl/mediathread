# pylint: disable-msg=R0904
from datetime import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from mediathread.djangosherd.models import SherdNote
from mediathread.factories import MediathreadTestMixin, \
    AssetFactory, SherdNoteFactory, ProjectFactory
from mediathread.projects.models import Project


class ProjectTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.setup_alternate_course()

        # Sample Course Image Asset
        self.asset1 = AssetFactory.create(course=self.sample_course,
                                          primary_source='image')

        self.student_note = SherdNoteFactory(
            asset=self.asset1, author=self.student_one,
            tags=',student_one_selection',
            body='student one selection note', range1=0, range2=1)
        self.student_ga = SherdNoteFactory(
            asset=self.asset1, author=self.student_one,
            tags=',student_one_item',
            body='student one item note',
            title=None, range1=None, range2=None)
        self.instructor_note = SherdNoteFactory(
            asset=self.asset1, author=self.instructor_one,
            tags=',image, instructor_one_selection,',
            body='instructor one selection note', range1=0, range2=1)
        self.instructor_ga = SherdNoteFactory(
            asset=self.asset1, author=self.instructor_one,
            tags=',image, instructor_one_item,',
            body='instructor one item note',
            title=None, range1=None, range2=None)

        # Sample Course Projects
        self.project_private = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PrivateEditorsAreOwners')

        self.project_instructor_shared = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='InstructorShared')

        self.project_class_shared = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='CourseProtected')

        self.assignment = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='Assignment')
        self.add_citation(self.assignment, self.student_note)
        self.add_citation(self.assignment, self.instructor_note)
        self.add_citation(self.assignment, self.student_ga)
        self.add_citation(self.assignment, self.instructor_ga)

    def test_description(self):

        project = Project.objects.get(id=self.project_private.id)
        self.assertEquals(project.description(), 'Composition')

        self.assertEquals(project.visibility_short(), 'Private')
        project = Project.objects.get(id=self.project_class_shared.id)
        self.assertEquals(project.visibility_short(), 'Published to Class')

        project = Project.objects.get(id=self.project_instructor_shared.id)
        self.assertEquals(project.visibility_short(),
                          'Submitted to Instructor')

        assignment = Project.objects.get(id=self.assignment.id)
        self.assertEquals(assignment.description(), 'Assignment')
        self.assertEquals(assignment.visibility_short(), 'Assignment')

    def test_migrate_one(self):
        new_project = Project.objects.migrate_one(self.project_private,
                                                  self.alt_course,
                                                  self.alt_instructor)

        self.assertEquals(new_project.title, self.project_private.title)
        self.assertEquals(new_project.author, self.alt_instructor)
        self.assertEquals(new_project.course, self.alt_course)
        self.assertEquals(new_project.visibility_short(), "Private")

        new_project = Project.objects.migrate_one(self.assignment,
                                                  self.alt_course,
                                                  self.alt_instructor)

        self.assertEquals(new_project.title, self.assignment.title)
        self.assertEquals(new_project.author, self.alt_instructor)
        self.assertEquals(new_project.course, self.alt_course)
        self.assertEquals(new_project.visibility_short(), "Assignment")

    def test_migrate_projects_to_alt_course(self):
        self.assertEquals(len(self.alt_course.asset_set.all()), 0)
        self.assertEquals(len(self.alt_course.project_set.all()), 0)

        projects = Project.objects.filter(id=self.assignment.id)

        object_map = {'assets': {}, 'notes': {}, 'projects': {}}
        object_map = Project.objects.migrate(projects, self.alt_course,
                                             self.alt_instructor,
                                             object_map,
                                             True, True)

        assets = self.alt_course.asset_set
        self.assertEquals(assets.count(), 1)
        asset = assets.all()[0]
        self.assertEquals(asset.title, self.asset1.title)

        self.assertEquals(asset.sherdnote_set.count(), 3)

        ga = asset.global_annotation(self.alt_instructor, auto_create=False)
        self.assertIsNotNone(asset.global_annotation(self.alt_instructor,
                                                     auto_create=False))
        self.assertEquals(ga.tags,
                          ',student_one_item,image, instructor_one_item,')
        self.assertEquals(ga.body,
                          'student one item noteinstructor one item note')

        asset.sherdnote_set.get(title=self.student_note.title)
        asset.sherdnote_set.get(title=self.instructor_note.title)

        self.assertEquals(self.alt_course.project_set.count(), 1)
        project = self.alt_course.project_set.all()[0]
        self.assertEquals(project.title, self.assignment.title)
        self.assertEquals(project.visibility_short(), 'Assignment')
        self.assertEquals(project.author, self.alt_instructor)

        citations = SherdNote.objects.references_in_string(project.body,
                                                           self.alt_instructor)
        self.assertEquals(len(citations), 4)

        self.assertEquals(citations[0].title, self.student_note.title)
        self.assertEquals(citations[0].author, self.alt_instructor)

        self.assertEquals(citations[1].title, self.instructor_note.title)
        self.assertEquals(citations[1].author, self.alt_instructor)

        self.assertEquals(citations[2].id, ga.id)
        self.assertEquals(citations[3].id, ga.id)

    def test_visible_by_course(self):
        visible_projects = Project.objects.visible_by_course(
            self.sample_course, self.student_one)
        self.assertEquals(len(visible_projects), 4)
        self.assertEquals(visible_projects[0], self.assignment)
        self.assertEquals(visible_projects[1], self.project_class_shared)
        self.assertEquals(visible_projects[2], self.project_instructor_shared)
        self.assertEquals(visible_projects[3], self.project_private)

        visible_projects = Project.objects.visible_by_course(
            self.sample_course, self.student_two)

        self.assertEquals(len(visible_projects), 2)
        self.assertEquals(visible_projects[0], self.assignment)
        self.assertEquals(visible_projects[1], self.project_class_shared)

        visible_projects = Project.objects.visible_by_course(
            self.sample_course, self.instructor_one)
        self.assertEquals(len(visible_projects), 3)
        self.assertEquals(visible_projects[0], self.assignment)
        self.assertEquals(visible_projects[1], self.project_class_shared)
        self.assertEquals(visible_projects[2], self.project_instructor_shared)

    def test_visible_by_course_and_user(self):
        visible_projects = Project.objects.visible_by_course_and_user(
            self.sample_course, self.student_one, self.student_one, False)
        self.assertEquals(len(visible_projects), 3)
        self.assertEquals(visible_projects[0], self.project_class_shared)
        self.assertEquals(visible_projects[1], self.project_instructor_shared)
        self.assertEquals(visible_projects[2], self.project_private)

        visible_projects = Project.objects.visible_by_course_and_user(
            self.sample_course, self.student_one, self.instructor_one, True)
        self.assertEquals(len(visible_projects), 1)
        self.assertEquals(visible_projects[0], self.assignment)

        visible_projects = Project.objects.visible_by_course_and_user(
            self.sample_course, self.student_two, self.student_one, False)
        self.assertEquals(len(visible_projects), 1)
        self.assertEquals(visible_projects[0], self.project_class_shared)

        visible_projects = Project.objects.visible_by_course_and_user(
            self.sample_course, self.instructor_one, self.student_one, False)
        self.assertEquals(len(visible_projects), 2)
        self.assertEquals(visible_projects[0], self.project_class_shared)
        self.assertEquals(visible_projects[1], self.project_instructor_shared)

    def test_project_clean_date_field(self):
        try:
            self.assignment.due_date = datetime(2012, 3, 13, 0, 0)
            self.assignment.clean()
            self.assertTrue(False, 'Due date is in the past')
        except ValidationError as err:
            self.assertTrue(
                err.messages[0].startswith('03/13/12 is not valid'))

        try:
            today = datetime.today()
            this_day = datetime(today.year, today.month, today.day, 0, 0)
            self.assignment.due_date = this_day
            self.assignment.clean()
        except ValidationError as err:
            self.assertTrue(False, "Due date is today. That's okay.")

        try:
            self.assignment.due_date = datetime(2020, 1, 1, 0, 0)
            self.assignment.clean()
        except ValidationError as err:
            self.assertTrue(False, "Due date is in the future, that's ok")

    def test_faculty_compositions(self):
        compositions = Project.objects.faculty_compositions(
            self.sample_course, self.student_one)
        self.assertEquals(len(compositions), 0)

        # instructor composition
        ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='CourseProtected')

        compositions = Project.objects.faculty_compositions(
            self.sample_course, self.student_one)
        self.assertEquals(len(compositions), 1)

    def test_responses(self):
        response1 = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='InstructorShared', parent=self.assignment)
        ProjectFactory.create(
            course=self.sample_course, author=self.student_two,
            policy='InstructorShared', parent=self.assignment)

        r = self.assignment.responses(self.sample_course, self.instructor_one)
        self.assertEquals(len(r), 2)

        r = self.assignment.responses_by(self.sample_course,
                                         self.instructor_one,
                                         self.student_one)
        self.assertEquals(r[0], response1)

    def test_reset_publish_to_world(self):
        public = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PublicEditorsAreOwners')
        self.assertEquals(public.public_url(), '/s/collaboration/7/')

        Project.objects.reset_publish_to_world(self.sample_course)
        self.assertIsNone(public.public_url())
