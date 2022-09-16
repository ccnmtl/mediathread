# pylint: disable-msg=R0904
from datetime import datetime, timedelta

from django.db import IntegrityError
from django.test import TestCase

from mediathread.djangosherd.models import SherdNote
from mediathread.factories import (
    MediathreadTestMixin,
    AssetFactory, SherdNoteFactory, ProjectFactory, AssignmentItemFactory
)
from mediathread.projects.tests.factories import ProjectSequenceAssetFactory
from mediathread.projects.models import (
    Project, RESPONSE_VIEW_NEVER,
    RESPONSE_VIEW_SUBMITTED, RESPONSE_VIEW_ALWAYS, AssignmentItem,
    PUBLISH_WHOLE_CLASS, PUBLISH_WHOLE_WORLD, PUBLISH_DRAFT,
    PUBLISH_INSTRUCTOR_SHARED, PROJECT_TYPE_SELECTION_ASSIGNMENT,
    PROJECT_TYPE_SEQUENCE_ASSIGNMENT)


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
            title=None, is_global_annotation=True)
        self.instructor_note = SherdNoteFactory(
            asset=self.asset1, author=self.instructor_one,
            tags=',image, instructor_one_selection,',
            body='instructor one selection note', range1=0, range2=1)
        self.instructor_ga = SherdNoteFactory(
            asset=self.asset1, author=self.instructor_one,
            tags=',image, instructor_one_item,',
            body='instructor one item note',
            title=None, is_global_annotation=True)

        # Sample Course Projects
        self.project_private = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy=PUBLISH_DRAFT[0])

        self.project_instructor_shared = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy=PUBLISH_INSTRUCTOR_SHARED[0],
            date_submitted=datetime.today())

        self.project_class_shared = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy=PUBLISH_WHOLE_CLASS[0])

        self.assignment = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy=PUBLISH_WHOLE_CLASS[0], project_type='assignment')
        self.add_citation(self.assignment, self.student_note)
        self.add_citation(self.assignment, self.instructor_note)
        self.add_citation(self.assignment, self.student_ga)
        self.add_citation(self.assignment, self.instructor_ga)

        self.selection_assignment = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy=PUBLISH_WHOLE_CLASS[0],
            project_type=PROJECT_TYPE_SELECTION_ASSIGNMENT)

        self.sequence_assignment = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy=PUBLISH_WHOLE_CLASS[0],
            project_type=PROJECT_TYPE_SEQUENCE_ASSIGNMENT)

        self.draft_assignment = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy=PUBLISH_DRAFT[0], project_type='assignment')

        self.discussion_assignment = ProjectFactory.create(
            course=self.sample_course,
            author=self.instructor_one,
            body='Discussion Assignment Body',
            policy=PUBLISH_WHOLE_CLASS[0],
            project_type='discussion-assignment'
        )
        Project.objects.make_discussion_assignment(
            self.discussion_assignment,
            self.discussion_assignment.course,
            self.discussion_assignment.author)

    def test_can_cite(self):
        # notes in an unsubmitted project are not citable regardless of viewer
        self.assertFalse(self.project_private.can_cite(
            self.sample_course, self.student_two))
        self.assertTrue(self.project_instructor_shared.can_cite(
            self.sample_course, self.student_two))

        # parent assignment: responses always visible
        response = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy=PUBLISH_WHOLE_CLASS[0], parent=self.selection_assignment,
            date_submitted=datetime.today())
        self.assertTrue(
            response.can_cite(self.sample_course, self.student_two))

        # parent assignment: responses never visible
        self.selection_assignment.response_view_policy = 'never'
        self.selection_assignment.save()
        self.assertFalse(
            response.can_cite(self.sample_course, self.student_two))

        # parent assignment: responses visible after due_date passes
        # or on viewer submit
        yesterday = datetime.today() + timedelta(-1)
        self.selection_assignment.response_view_policy = 'submitted'
        self.selection_assignment.due_date = yesterday
        self.selection_assignment.save()
        self.assertTrue(
            response.can_cite(self.sample_course, self.student_two))

        tomorrow = datetime.today() + timedelta(1)
        self.selection_assignment.due_date = tomorrow
        self.selection_assignment.save()
        self.assertFalse(
            response.can_cite(self.sample_course, self.student_two))

        response = ProjectFactory.create(
            course=self.sample_course, author=self.student_two,
            policy=PUBLISH_WHOLE_CLASS[0], parent=self.selection_assignment,
            date_submitted=datetime.today())
        self.assertFalse(response.can_cite(
            self.sample_course, self.student_two))

        response = ProjectFactory.create(
            course=self.sample_course, author=self.student_three,
            policy=PUBLISH_WHOLE_CLASS[0], parent=self.selection_assignment,
            date_submitted=datetime.today())
        self.assertTrue(response.can_cite(
            self.sample_course, self.student_two))

    def test_description(self):
        project = Project.objects.get(id=self.project_private.id)
        self.assertEquals(project.description(), 'Composition')
        self.assertEquals(project.visibility_short(), 'Draft')

        project = Project.objects.get(id=self.project_class_shared.id)
        self.assertEquals(project.description(), 'Composition')
        self.assertEquals(project.visibility_short(), 'Shared with Class')

        project = Project.objects.get(id=self.project_instructor_shared.id)
        self.assertEquals(project.description(), 'Composition')
        self.assertEquals(project.visibility_short(),
                          'Shared with Instructor')

        assignment = Project.objects.get(id=self.assignment.id)
        self.assertEquals(assignment.description(), 'Composition Assignment')
        self.assertEquals(assignment.visibility_short(), 'Shared with Class')

        sassignment = Project.objects.get(id=self.selection_assignment.id)
        self.assertEquals(sassignment.description(), 'Selection Assignment')

        r = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            parent=self.selection_assignment)
        self.assertEquals(r.description(), 'Selection Assignment Response')

        r = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            parent=self.assignment)
        self.assertEquals(r.description(), 'Composition Assignment Response')

        r = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            parent=self.sequence_assignment)
        self.assertEquals(r.description(), 'Sequence Assignment Response')

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
        self.assertEquals(new_project.summary, self.assignment.summary)
        self.assertEquals(new_project.body, self.assignment.body)
        self.assertEquals(new_project.author, self.alt_instructor)
        self.assertEquals(new_project.course, self.alt_course)
        self.assertEquals(new_project.description(), 'Composition Assignment')
        self.assertEquals(new_project.visibility_short(), 'Shared with Class')
        self.assertEquals(AssignmentItem.objects.count(), 0)

    def test_migrate_one_discussion_assignment(self):
        self.assertIsNotNone(self.discussion_assignment.get_collaboration())
        self.assertTrue(self.discussion_assignment.is_discussion_assignment())
        discussion = self.discussion_assignment.course_discussion()
        self.assertIsNotNone(discussion)

        new_project = Project.objects.migrate_one(
            self.discussion_assignment,
            self.alt_course,
            self.alt_instructor)

        self.assertEqual(new_project.title, self.discussion_assignment.title)
        self.assertEqual(
            new_project.summary,
            self.discussion_assignment.summary)
        self.assertEqual(
            new_project.body,
            self.discussion_assignment.body)
        self.assertEqual(new_project.author, self.alt_instructor)
        self.assertEqual(new_project.course, self.alt_course)
        self.assertEqual(
            new_project.visibility_short(), 'Shared with Class')

        collab = new_project.get_collaboration()
        self.assertIsNotNone(collab)
        new_discussion = new_project.course_discussion()
        self.assertIsNotNone(new_discussion)
        self.assertEqual(discussion.title, new_discussion.title)
        self.assertEqual(discussion.comment, new_discussion.comment)

        # Assert that the original discussion's body text made it through
        # to the ThreadedComment's comment attribute.
        self.assertEqual(discussion.comment, self.discussion_assignment.body)

        self.assertEqual(discussion.user, self.instructor_one)
        self.assertEqual(new_discussion.user, self.alt_instructor)

    def test_migrate_selection_assignment(self):
        assignment1 = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy=PUBLISH_WHOLE_CLASS[0], title="Assignment 1",
            response_view_policy=RESPONSE_VIEW_NEVER[0],
            project_type='selection-assignment')
        assignment2 = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy=PUBLISH_WHOLE_CLASS[0], title="Assignment 2",
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
        self.assertEquals(project.visibility_short(), 'Shared with Class')
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
        self.assertEquals(len(visible_projects), 7)
        self.assertTrue(self.assignment in visible_projects)
        self.assertTrue(self.selection_assignment in visible_projects)
        self.assertTrue(self.sequence_assignment in visible_projects)
        self.assertTrue(self.project_class_shared in visible_projects)
        self.assertTrue(self.project_instructor_shared in visible_projects)
        self.assertTrue(self.project_private in visible_projects)

        visible_projects = Project.objects.visible_by_course(
            self.sample_course, self.student_two)

        self.assertEquals(len(visible_projects), 5)
        self.assertTrue(self.assignment in visible_projects)
        self.assertTrue(self.selection_assignment in visible_projects)
        self.assertTrue(self.sequence_assignment in visible_projects)
        self.assertTrue(self.project_class_shared, visible_projects)

        visible_projects = Project.objects.visible_by_course(
            self.sample_course, self.instructor_one)
        self.assertEquals(len(visible_projects), 7)
        self.assertTrue(self.assignment in visible_projects)
        self.assertTrue(self.draft_assignment in visible_projects)
        self.assertTrue(self.project_class_shared in visible_projects)
        self.assertTrue(self.project_instructor_shared in visible_projects)
        self.assertTrue(self.selection_assignment in visible_projects)
        self.assertTrue(self.sequence_assignment in visible_projects)

    def test_visible_by_course_and_user(self):
        visible_projects = Project.objects.visible_by_course_and_user(
            self.sample_course, self.student_one, self.student_one, False)
        self.assertEquals(len(visible_projects), 3)
        self.assertEquals(visible_projects[0], self.project_class_shared)
        self.assertEquals(visible_projects[1], self.project_instructor_shared)
        self.assertEquals(visible_projects[2], self.project_private)

        visible_projects = Project.objects.visible_by_course_and_user(
            self.sample_course, self.student_one, self.instructor_one, True)
        self.assertEquals(len(visible_projects), 4)
        self.assertTrue(self.assignment in visible_projects)
        self.assertTrue(self.selection_assignment in visible_projects)
        self.assertTrue(self.sequence_assignment in visible_projects)

        visible_projects = Project.objects.visible_by_course_and_user(
            self.sample_course, self.student_two, self.student_one, False)
        self.assertEquals(len(visible_projects), 1)
        self.assertEquals(visible_projects[0], self.project_class_shared)

        visible_projects = Project.objects.visible_by_course_and_user(
            self.sample_course, self.instructor_one, self.student_one, False)
        self.assertEquals(len(visible_projects), 2)
        self.assertEquals(visible_projects[0], self.project_class_shared)
        self.assertEquals(visible_projects[1], self.project_instructor_shared)

    def test_projects_visible_by_course_and_owner(self):
        visible = Project.objects.projects_visible_by_course_and_owner(
            self.sample_course, self.student_one, self.student_one)
        self.assertEquals(len(visible), 3)
        self.assertTrue(self.project_class_shared in visible)
        self.assertTrue(self.project_instructor_shared in visible)
        self.assertTrue(self.project_private in visible)

        visible = Project.objects.projects_visible_by_course_and_owner(
            self.sample_course, self.student_one, self.instructor_one)
        self.assertEquals(len(visible), 0)

        visible = Project.objects.projects_visible_by_course_and_owner(
            self.sample_course, self.student_two, self.student_one)
        self.assertEquals(len(visible), 1)
        self.assertEquals(visible[0], self.project_class_shared)

        visible = Project.objects.projects_visible_by_course_and_owner(
            self.sample_course, self.instructor_one, self.student_one)
        self.assertEquals(len(visible), 2)
        self.assertTrue(self.project_class_shared in visible)
        self.assertTrue(self.project_instructor_shared in visible)

    def assert_responses_by_course(self, viewer, visible, hidden):
        visible_responses, hidden_responses = \
            Project.objects.responses_by_course(self.sample_course, viewer)

        for response in visible:
            self.assertTrue(response in visible_responses)
            self.assertTrue(response not in hidden_responses)

        for response in hidden:
            self.assertTrue(response not in visible_responses)
            self.assertTrue(response in hidden_responses)

    def test_responses_by_course(self):
        # no responses
        self.assert_responses_by_course(self.student_one, [], [])
        self.assert_responses_by_course(self.instructor_one, [], [])

        # private response
        response = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy=PUBLISH_DRAFT[0], parent=self.assignment)

        self.assert_responses_by_course(self.student_one, [response], [])
        self.assert_responses_by_course(self.instructor_one, [], [response])
        self.assert_responses_by_course(self.student_two, [], [response])

        # submit response
        response.create_or_update_collaboration(PUBLISH_WHOLE_CLASS[0])
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
            date_submitted=datetime.now(), policy=PUBLISH_WHOLE_CLASS[0],
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
            date_submitted=datetime.now(), policy=PUBLISH_WHOLE_CLASS[0],
            parent=self.assignment)

        # private response
        response2 = ProjectFactory.create(
            title='Omega', course=self.sample_course, author=self.student_one,
            policy=PUBLISH_DRAFT[0], parent=self.assignment)

        response4 = ProjectFactory.create(
            title='Gam', course=self.sample_course, author=self.student_three,
            date_submitted=datetime.now(), policy=PUBLISH_WHOLE_CLASS[0],
            parent=self.assignment)
        response4.delete()

        response3 = ProjectFactory.create(
            title='Beta', course=self.sample_course, author=self.student_two,
            date_submitted=datetime.now(), policy=PUBLISH_WHOLE_CLASS[0],
            parent=self.assignment)

        self.assert_responses_by_course(self.student_one,
                                        [response3, response1, response2], [])
        self.assert_responses_by_course(self.instructor_one,
                                        [response3, response1], [response2])
        self.assert_responses_by_course(self.student_two,
                                        [response3, response1], [response2])

    def test_faculty_compositions(self):
        compositions = Project.objects.faculty_compositions(
            self.sample_course, self.student_one)
        self.assertEquals(len(compositions), 0)

        # instructor composition
        beta = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy=PUBLISH_WHOLE_CLASS[0], ordinality=2, title='Beta')
        gamma = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy=PUBLISH_WHOLE_CLASS[0], ordinality=3, title='Gamma')
        alpha = ProjectFactory.create(
            course=self.sample_course, author=self.instructor_one,
            policy=PUBLISH_WHOLE_CLASS[0], ordinality=1, title='Alpha')

        compositions = Project.objects.faculty_compositions(
            self.sample_course, self.student_one)
        self.assertEquals(len(compositions), 3)
        self.assertEquals(compositions[0], alpha)
        self.assertEquals(compositions[1], beta)
        self.assertEquals(compositions[2], gamma)

    def test_responses(self):
        response1 = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy=PUBLISH_INSTRUCTOR_SHARED[0], parent=self.assignment)
        response2 = ProjectFactory.create(
            course=self.sample_course, author=self.student_two,
            policy=PUBLISH_INSTRUCTOR_SHARED[0], parent=self.assignment)

        r = self.assignment.responses(self.sample_course, self.instructor_one)
        self.assertEquals(len(r), 2)

        r = self.assignment.responses(self.sample_course, self.instructor_one,
                                      self.student_one)
        self.assertEquals(r[0], response1)

        r = self.assignment.responses(self.sample_course, self.instructor_one,
                                      self.student_two)
        self.assertEquals(r[0], response2)

    def test_responses_for_bad_assignment_state(self):
        ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy=PUBLISH_INSTRUCTOR_SHARED[0], parent=self.assignment)
        self.assignment.get_collaboration().delete()

        r = self.assignment.responses(self.sample_course, self.instructor_one)
        self.assertEquals(len(r), 0)

    def test_reset_publish_to_world(self):
        public = ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy=PUBLISH_WHOLE_WORLD[0])
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
                          PUBLISH_DRAFT[0])

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

        project.create_or_update_collaboration(PUBLISH_DRAFT[0])
        collaboration = project.get_collaboration()
        self.assertEquals(collaboration.policy_record.policy_name,
                          PUBLISH_DRAFT[0])

        project.create_or_update_collaboration(PUBLISH_WHOLE_CLASS[0])
        collaboration = project.get_collaboration()
        self.assertEquals(collaboration.policy_record.policy_name,
                          PUBLISH_WHOLE_CLASS[0])

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
            policy=PUBLISH_WHOLE_CLASS[0],
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
        response2.create_or_update_collaboration(PUBLISH_WHOLE_CLASS[0])
        response2.date_submitted = datetime.now()
        response2.save()
        self.assertTrue(response.can_read(
            self.sample_course, self.student_two))

    def test_can_read_selection_assignment_response(self):
        self.can_read_assignment_response(self.selection_assignment)

    def test_can_read_composition_assignment_response(self):
        self.can_read_assignment_response(self.assignment)

    def test_visible_assignments_by_course_student(self):
        lst = Project.objects.visible_assignments_by_course(
            self.sample_course, self.student_one)
        self.assertEquals(len(lst), 4)
        self.assertTrue(self.selection_assignment in lst)
        self.assertTrue(self.sequence_assignment in lst)
        self.assertTrue(self.assignment in lst)

    def test_visible_assignments_by_course_faculty(self):
        lst = Project.objects.visible_assignments_by_course(
            self.sample_course, self.instructor_one)
        self.assertEquals(len(lst), 5)
        self.assertTrue(self.selection_assignment in lst)
        self.assertTrue(self.sequence_assignment in lst)
        self.assertTrue(self.assignment in lst)
        self.assertTrue(self.draft_assignment in lst)

    def test_unresponded_assignments(self):
        lst = Project.objects.unresponded_assignments(self.sample_course,
                                                      self.student_one)
        self.assertEquals(len(lst), 4)
        self.assertTrue(self.selection_assignment in lst)
        self.assertTrue(self.sequence_assignment in lst)
        self.assertTrue(self.assignment in lst)

        # add a response & retry
        ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy=PUBLISH_WHOLE_CLASS[0],
            parent=self.selection_assignment)

        lst = Project.objects.unresponded_assignments(self.sample_course,
                                                      self.student_one)
        self.assertEquals(len(lst), 3)
        self.assertTrue(self.assignment in lst)
        self.assertTrue(self.sequence_assignment in lst)

        # add a response & retry
        ProjectFactory.create(
            course=self.sample_course, author=self.student_one,
            policy=PUBLISH_DRAFT[0],
            parent=self.assignment)

        lst = Project.objects.unresponded_assignments(self.sample_course,
                                                      self.student_one)
        self.assertEquals(len(lst), 2)
        self.assertTrue(self.sequence_assignment in lst)

    def test_is_participant(self):
        self.assertTrue(self.project_private.is_participant(self.student_one))
        self.assertFalse(self.project_private.is_participant(self.student_two))

        self.project_private.participants.add(self.student_two)
        self.assertTrue(self.project_private.is_participant(self.student_two))

    def test_visibility_policy(self):
        self.assertEqual(
            self.project_private.visibility_policy(),
            'PrivateEditorsAreOwners')

    def test_visibility(self):
        self.assertEqual(
            self.project_private.visibility(), 'Draft - only you can view')

    def test_visibility_short(self):
        self.assertEqual(self.project_private.visibility_short(), 'Draft')

    def test_visibility_status(self):
        self.assertEqual(self.project_private.status(), 'Draft')


class ProjectSequenceAssetTest(TestCase):
    def setUp(self):
        self.psa = ProjectSequenceAssetFactory()

    def test_is_valid_from_factory(self):
        self.psa.full_clean()

    def test_prevent_duplicate(self):
        with self.assertRaises(IntegrityError):
            ProjectSequenceAssetFactory(
                sequence_asset=self.psa.sequence_asset,
                project=self.psa.project)
