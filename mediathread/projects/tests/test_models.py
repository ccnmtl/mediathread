# pylint: disable-msg=R0904
from datetime import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from mediathread.djangosherd.models import SherdNote
from mediathread.factories import MediathreadTestMixin, \
    AssetFactory, SherdNoteFactory, ProjectFactory, AssignmentItemFactory
from mediathread.projects.models import Project, RESPONSE_VIEW_NEVER, \
    RESPONSE_VIEW_SUBMITTED, RESPONSE_VIEW_ALWAYS, AssignmentItem


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
            policy='CourseProtected', project_type='assignment')
        self.add_citation(self.assignment, self.student_note)
        self.add_citation(self.assignment, self.instructor_note)
        self.add_citation(self.assignment, self.student_ga)
        self.add_citation(self.assignment, self.instructor_ga)

        self.selection_assignment = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='CourseProtected', project_type='selection-assignment')

        self.draft_assignment = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='PrivateEditorsAreOwners', project_type='assignment')

    def test_description(self):
        project = Project.objects.get(id=self.project_private.id)
        self.assertEquals(project.description(), 'Composition')
        self.assertEquals(project.visibility_short(), 'Draft')

        project = Project.objects.get(id=self.project_class_shared.id)
        self.assertEquals(project.description(), 'Composition')
        self.assertEquals(project.visibility_short(), 'Published to Class')

        project = Project.objects.get(id=self.project_instructor_shared.id)
        self.assertEquals(project.description(), 'Composition')
        self.assertEquals(project.visibility_short(),
                          'Submitted to Instructor')

        assignment = Project.objects.get(id=self.assignment.id)
        self.assertEquals(assignment.description(), 'Composition Assignment')
        self.assertEquals(assignment.visibility_short(), 'Published to Class')

        sassignment = Project.objects.get(id=self.selection_assignment.id)
        self.assertEquals(sassignment.description(), 'Selection Assignment')

    def test_migrate_one(self):
        new_project = Project.objects.migrate_one(self.project_private,
                                                  self.alt_course,
                                                  self.alt_instructor)

        self.assertEquals(new_project.title, self.project_private.title)
        self.assertEquals(new_project.author, self.alt_instructor)
        self.assertEquals(new_project.course, self.alt_course)
        self.assertEquals(new_project.visibility_short(), "Draft")

        new_project = Project.objects.migrate_one(self.assignment,
                                                  self.alt_course,
                                                  self.alt_instructor)

        self.assertEquals(new_project.title, self.assignment.title)
        self.assertEquals(new_project.author, self.alt_instructor)
        self.assertEquals(new_project.course, self.alt_course)
        self.assertEquals(new_project.description(), 'Composition Assignment')
        self.assertEquals(new_project.visibility_short(), 'Published to Class')
        self.assertEquals(AssignmentItem.objects.count(), 0)

    def test_migrate_selection_assignment(self):
        assignment1 = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='CourseProtected', title="Assignment 1",
            response_view_policy=RESPONSE_VIEW_NEVER[0],
            project_type='selection-assignment')
        assignment2 = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='CourseProtected', title="Assignment 2",
            project_type='selection-assignment')

        asset = AssetFactory.create(course=self.sample_course,
                                    title='Sample', primary_source='image')

        AssignmentItemFactory.create(project=assignment1, asset=asset)
        AssignmentItemFactory.create(project=assignment2, asset=asset)

        projects = [assignment1, assignment2]
        object_map = {'assets': {}, 'notes': {}, 'projects': {}}
        object_map = Project.objects.migrate(
            projects, self.alt_course, self.alt_instructor,
            object_map, True, True)

        self.assertEquals(self.alt_course.asset_set.count(), 1)
        alt_asset = self.alt_course.asset_set.first()
        self.assertTrue(alt_asset.title, 'Sample')
        self.assertNotEqual(alt_asset.id, asset.id)

        self.assertEquals(self.alt_course.project_set.count(), 2)

        a = Project.objects.get(course=self.alt_course, title='Assignment 1')
        self.assertEquals(a.response_view_policy, RESPONSE_VIEW_NEVER[0])
        ai = AssignmentItem.objects.get(project=a)
        self.assertEquals(ai.asset, alt_asset)

        a = Project.objects.get(course=self.alt_course, title='Assignment 2')
        ai = AssignmentItem.objects.get(project=a)
        self.assertEquals(ai.asset, alt_asset)

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
        self.assertEquals(project.description(), 'Composition Assignment')
        self.assertEquals(project.visibility_short(), 'Published to Class')
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
        self.assertEquals(len(visible_projects), 5)
        self.assertTrue(self.assignment in visible_projects)
        self.assertTrue(self.selection_assignment in visible_projects)
        self.assertTrue(self.project_class_shared in visible_projects)
        self.assertTrue(self.project_instructor_shared in visible_projects)
        self.assertTrue(self.project_private in visible_projects)

        visible_projects = Project.objects.visible_by_course(
            self.sample_course, self.student_two)

        self.assertEquals(len(visible_projects), 3)
        self.assertTrue(self.assignment in visible_projects)
        self.assertTrue(self.selection_assignment in visible_projects)
        self.assertTrue(self.project_class_shared, visible_projects)

        visible_projects = Project.objects.visible_by_course(
            self.sample_course, self.instructor_one)
        self.assertEquals(len(visible_projects), 5)
        self.assertTrue(self.assignment in visible_projects)
        self.assertTrue(self.draft_assignment in visible_projects)
        self.assertTrue(self.project_class_shared in visible_projects)
        self.assertTrue(self.project_instructor_shared in visible_projects)
        self.assertTrue(self.selection_assignment in visible_projects)

    def test_visible_by_course_and_user(self):
        visible_projects = Project.objects.visible_by_course_and_user(
            self.sample_course, self.student_one, self.student_one, False)
        self.assertEquals(len(visible_projects), 3)
        self.assertEquals(visible_projects[0], self.project_class_shared)
        self.assertEquals(visible_projects[1], self.project_instructor_shared)
        self.assertEquals(visible_projects[2], self.project_private)

        visible_projects = Project.objects.visible_by_course_and_user(
            self.sample_course, self.student_one, self.instructor_one, True)
        self.assertEquals(len(visible_projects), 2)
        self.assertTrue(self.assignment in visible_projects)
        self.assertTrue(self.selection_assignment in visible_projects)

        visible_projects = Project.objects.visible_by_course_and_user(
            self.sample_course, self.student_two, self.student_one, False)
        self.assertEquals(len(visible_projects), 1)
        self.assertEquals(visible_projects[0], self.project_class_shared)

        visible_projects = Project.objects.visible_by_course_and_user(
            self.sample_course, self.instructor_one, self.student_one, False)
        self.assertEquals(len(visible_projects), 2)
        self.assertEquals(visible_projects[0], self.project_class_shared)
        self.assertEquals(visible_projects[1], self.project_instructor_shared)

    def assert_responses_by_course(self, viewer, visible, hidden):
        self.assertEquals(
            Project.objects.responses_by_course(self.sample_course, viewer),
            (visible, hidden))

    def test_responses_by_course(self):
        # no responses
        self.assert_responses_by_course(self.student_one, [], [])
        self.assert_responses_by_course(self.instructor_one, [], [])

        # private response
        response = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PrivateEditorsAreOwners', parent=self.assignment)

        self.assert_responses_by_course(self.student_one, [response], [])
        self.assert_responses_by_course(self.instructor_one, [], [response])
        self.assert_responses_by_course(self.student_two, [], [response])

        # submit response
        response.create_or_update_collaboration('PublicEditorsAreOwners')
        response.date_submitted = datetime.now()
        response.save()

        self.assert_responses_by_course(self.student_one, [response], [])
        self.assert_responses_by_course(self.instructor_one, [response], [])
        self.assert_responses_by_course(self.student_two, [response], [])

        # change assignment policy to never
        self.assignment.response_view_policy = RESPONSE_VIEW_NEVER[0]
        self.assignment.save()

        self.assert_responses_by_course(self.student_one, [response], [])
        self.assert_responses_by_course(self.instructor_one, [response], [])
        self.assert_responses_by_course(self.student_two, [], [response])

        # change assignment policy to submitted
        self.assignment.response_view_policy = RESPONSE_VIEW_SUBMITTED[0]
        self.assignment.save()

        self.assert_responses_by_course(self.student_one, [response], [])
        self.assert_responses_by_course(self.instructor_one, [response], [])
        self.assert_responses_by_course(self.student_two, [], [response])

        # student_two submits
        response2 = ProjectFactory.create(
            course=self.sample_course, author=self.student_two,
            date_submitted=datetime.now(), policy='PublicEditorsAreOwners',
            parent=self.assignment)
        self.assert_responses_by_course(self.student_one,
                                        [response, response2], [])
        self.assert_responses_by_course(self.instructor_one,
                                        [response, response2], [])
        self.assert_responses_by_course(self.student_two,
                                        [response, response2], [])

    def test_many_responses_by_course(self):
        # additional responses ensure selected collaborations/projects
        # don't line-up by default
        response1 = ProjectFactory.create(
            title='Zeta', course=self.sample_course, author=self.student_three,
            date_submitted=datetime.now(), policy='PublicEditorsAreOwners',
            parent=self.assignment)

        # private response
        response2 = ProjectFactory.create(
            title='Omega', course=self.sample_course, author=self.student_one,
            policy='PrivateEditorsAreOwners', parent=self.assignment)

        response4 = ProjectFactory.create(
            title='Gam', course=self.sample_course, author=self.student_three,
            date_submitted=datetime.now(), policy='PublicEditorsAreOwners',
            parent=self.assignment)
        response4.delete()

        response3 = ProjectFactory.create(
            title='Beta', course=self.sample_course, author=self.student_two,
            date_submitted=datetime.now(), policy='PublicEditorsAreOwners',
            parent=self.assignment)

        self.assert_responses_by_course(self.student_one,
                                        [response3, response1, response2], [])
        self.assert_responses_by_course(self.instructor_one,
                                        [response3, response1], [response2])
        self.assert_responses_by_course(self.student_two,
                                        [response3, response1], [response2])

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
        beta = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='CourseProtected', ordinality=2, title='Beta')
        gamma = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='CourseProtected', ordinality=3, title='Gamma')
        alpha = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy='CourseProtected', ordinality=1, title='Alpha')

        compositions = Project.objects.faculty_compositions(
            self.sample_course, self.student_one)
        self.assertEquals(len(compositions), 3)
        self.assertEquals(compositions[0], alpha)
        self.assertEquals(compositions[1], beta)
        self.assertEquals(compositions[2], gamma)

    def test_responses(self):
        response1 = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='InstructorShared', parent=self.assignment)
        response2 = ProjectFactory.create(
            course=self.sample_course, author=self.student_two,
            policy='InstructorShared', parent=self.assignment)

        r = self.assignment.responses(self.sample_course, self.instructor_one)
        self.assertEquals(len(r), 2)

        r = self.assignment.responses(self.sample_course, self.instructor_one,
                                      self.student_one)
        self.assertEquals(r[0], response1)

        r = self.assignment.responses(self.sample_course, self.instructor_one,
                                      self.student_two)
        self.assertEquals(r[0], response2)

    def test_reset_publish_to_world(self):
        public = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PublicEditorsAreOwners')
        self.assertEquals(
            public.public_url(),
            '/s/%s/project/%s/' % (self.sample_course.slug(), public.id))

        Project.objects.reset_publish_to_world(self.sample_course)
        self.assertIsNone(public.public_url())

    def test_limit_response_policy(self):
        self.assertEquals(self.assignment.response_view_policy,
                          RESPONSE_VIEW_ALWAYS[0])
        self.assertEquals(self.selection_assignment.response_view_policy,
                          RESPONSE_VIEW_ALWAYS[0])
        Project.objects.limit_response_policy(self.sample_course)

        assignment = Project.objects.get(id=self.assignment.id)
        self.assertEquals(assignment.response_view_policy,
                          RESPONSE_VIEW_NEVER[0])
        assignment = Project.objects.get(id=self.selection_assignment.id)
        self.assertEquals(assignment.response_view_policy,
                          RESPONSE_VIEW_NEVER[0])

    def test_collaboration_sync_model(self):
        project = ProjectFactory.create(
            course=self.sample_course, author=self.student_one)

        collaboration = project.get_collaboration()
        self.assertEquals(collaboration.policy_record.policy_name,
                          'PrivateEditorsAreOwners')

        project.collaboration_sync_group(collaboration)
        self.assertIsNotNone(collaboration.group)
        users = collaboration.group.user_set.all()
        self.assertEquals(users.count(), 1)
        self.assertTrue(self.student_one in users)

        # add some participants
        project.participants.add(self.student_two)
        project.collaboration_sync_group(collaboration)
        self.assertIsNotNone(collaboration.group)
        users = collaboration.group.user_set.all()
        self.assertEquals(users.count(), 2)
        self.assertTrue(self.student_one in users)
        self.assertTrue(self.student_two in users)

        # remove some participants
        project.participants.remove(self.student_two)
        project.collaboration_sync_group(collaboration)
        self.assertIsNotNone(collaboration.group)
        users = collaboration.group.user_set.all()
        self.assertEquals(users.count(), 1)
        self.assertTrue(self.student_one in users)
        self.assertFalse(self.student_two in users)

    def test_collaboration_create_or_update(self):
        project = Project.objects.create(title="Untitled",
                                         course=self.sample_course,
                                         author=self.student_one)
        self.assertIsNone(project.get_collaboration())

        project.create_or_update_collaboration('PrivateEditorsAreOwners')
        collaboration = project.get_collaboration()
        self.assertEquals(collaboration.policy_record.policy_name,
                          'PrivateEditorsAreOwners')

        project.create_or_update_collaboration('PublicEditorsAreOwners')
        collaboration = project.get_collaboration()
        self.assertEquals(collaboration.policy_record.policy_name,
                          'PublicEditorsAreOwners')

    def test_create_or_update_item(self):
        project = ProjectFactory.create(
            course=self.sample_course, author=self.student_one)

        project.create_or_update_item(self.asset1.id)
        self.assertEquals(project.assignmentitem_set.first().asset,
                          self.asset1)

        asset2 = AssetFactory.create(course=self.sample_course,
                                     primary_source='youtube')

        project.create_or_update_item(asset2.id)
        self.assertEquals(project.assignmentitem_set.first().asset, asset2)

    def test_set_parent(self):
        project = ProjectFactory.create(
            course=self.sample_course, author=self.student_one)
        self.assertIsNone(project.assignment())

        project.set_parent(self.assignment.id)
        self.assertEquals(project.assignment(), self.assignment)

    def test_can_read(self):
        self.assertTrue(self.project_private.can_read(
            self.sample_course, self.student_one))
        self.assertFalse(self.project_private.can_read(
            self.sample_course, self.student_two))
        self.assertFalse(self.project_private.can_read(
            self.sample_course, self.instructor_one))
        self.assertFalse(self.project_private.can_read(
            self.alt_course, self.alt_instructor))

        self.assertTrue(self.project_instructor_shared.can_read(
            self.sample_course, self.student_one))
        self.assertFalse(self.project_instructor_shared.can_read(
            self.sample_course, self.student_two))
        self.assertTrue(self.project_instructor_shared.can_read(
            self.sample_course, self.instructor_one))
        self.assertFalse(self.project_instructor_shared.can_read(
            self.sample_course, self.alt_instructor))

        self.assertTrue(self.project_class_shared.can_read(
            self.sample_course, self.student_one))
        self.assertTrue(self.project_class_shared.can_read(
            self.sample_course, self.student_two))
        self.assertTrue(self.project_class_shared.can_read(
            self.sample_course, self.instructor_one))
        self.assertFalse(self.project_class_shared.can_read(
            self.alt_course, self.alt_instructor))

    def can_read_assignment_response(self, parent):
        # always
        response = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PublicEditorsAreOwners',
            parent=parent)

        self.assertTrue(response.can_read(
            self.sample_course, self.student_one))
        self.assertTrue(response.can_read(
            self.sample_course, self.student_two))
        self.assertTrue(response.can_read(
            self.sample_course, self.instructor_one))

        # never
        parent.response_view_policy = \
            RESPONSE_VIEW_NEVER[0]
        parent.save()

        self.assertTrue(response.can_read(
            self.sample_course, self.student_one))
        self.assertFalse(response.can_read(
            self.sample_course, self.student_two))
        self.assertTrue(response.can_read(
            self.sample_course, self.instructor_one))

        # submitted
        parent.response_view_policy = \
            RESPONSE_VIEW_SUBMITTED[0]
        parent.save()

        self.assertTrue(response.can_read(
            self.sample_course, self.student_one))
        self.assertFalse(response.can_read(
            self.sample_course, self.student_two))
        self.assertTrue(response.can_read(
            self.sample_course, self.instructor_one))

        # student two created a response
        response2 = ProjectFactory.create(
            course=self.sample_course, author=self.student_two,
            parent=parent)
        self.assertFalse(response.can_read(
            self.sample_course, self.student_two))

        # student two submits his response (mock)
        response2.create_or_update_collaboration('PublicEditorsAreOwners')
        response2.date_submitted = datetime.now()
        response2.save()
        self.assertTrue(response.can_read(
            self.sample_course, self.student_two))

    def test_can_read_selection_assignment_response(self):
        self.can_read_assignment_response(self.selection_assignment)

    def test_can_read_composition_assignment_response(self):
        self.can_read_assignment_response(self.assignment)

    def test_unresponded_assignments(self):
        lst = Project.objects.unresponded_assignments(self.sample_course,
                                                      self.student_one)
        self.assertEquals(len(lst), 2)
        self.assertTrue(self.selection_assignment in lst)
        self.assertTrue(self.assignment in lst)

        # add a response & retry
        ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PublicEditorsAreOwners',
            parent=self.selection_assignment)

        lst = Project.objects.unresponded_assignments(self.sample_course,
                                                      self.student_one)
        self.assertEquals(len(lst), 1)
        self.assertTrue(self.assignment in lst)

        # add a response & retry
        ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy='PrivateEditorsAreOwners',
            parent=self.assignment)

        lst = Project.objects.unresponded_assignments(self.sample_course,
                                                      self.student_one)
        self.assertEquals(len(lst), 0)

    def test_is_participant(self):
        self.assertTrue(self.project_private.is_participant(self.student_one))
        self.assertFalse(self.project_private.is_participant(self.student_two))

        self.project_private.participants.add(self.student_two)
        self.assertTrue(self.project_private.is_participant(self.student_two))
