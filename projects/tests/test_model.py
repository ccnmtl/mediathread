from assetmgr.models import Asset
from courseaffils.models import Course
from django.contrib.auth.models import User
from django.test import TestCase
from djangosherd.models import SherdNote
from projects.models import Project
import simplejson


class ProjectTest(TestCase):
    fixtures = ['unittest_sample_course.json',
                'unittest_sample_projects.json']

    def test_migrate_one(self):
        alt_course = Course.objects.get(id=2)
        self.assertEquals(alt_course.title, "Alternate Course")

        alt_instructor = User.objects.get(username='test_instructor_alt')

        private_essay = Project.objects.get(id=1)
        x = Project.objects.migrate_one(private_essay,
                                        alt_course,
                                        alt_instructor)

        self.assertEquals(x.title, "Private Composition")
        self.assertEquals(x.author, alt_instructor)
        self.assertEquals(x.course, alt_course)
        self.assertEquals(x.visibility_short(), "Private")

        assignment = Project.objects.get(id=5)
        x = Project.objects.migrate_one(assignment,
                                        alt_course,
                                        alt_instructor)

        self.assertEquals(x.title, "Sample Course Assignment")
        self.assertEquals(x.author, alt_instructor)
        self.assertEquals(x.course, alt_course)
        self.assertEquals(x.visibility_short(), "Assignment")

    project_set = [{"id": 5,
                    "title":"Sample Course Assignment"}]

    def test_migrate_set(self):
        self.assertTrue(True)

        course = Course.objects.get(id=2)
        self.assertEquals(course.title, "Alternate Course")
        self.assertEquals(len(course.asset_set.all()), 1)
        self.assertEquals(len(course.project_set.all()), 1)

        user = User.objects.get(username='test_instructor_two')

        project_json = simplejson.dumps(self.project_set)
        projects = simplejson.loads(project_json)

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

        self.assertEquals(len(course.project_set.all()), 2)
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

        # Another user's global annotation
        self.assertTrue(citations[1].asset.title,
                        "Mediathread: Introduction")
        self.assertEquals(citations[1].id,
                          citations[1].asset.global_annotation(user, False).id)
        self.assertEquals(citations[1].tags, '')

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

        # Onw asset
        self.assertTrue(citations[3].asset.title, "Project Portfolio")
        self.assertTrue(citations[3].is_global_annotation())
        self.assertEquals(citations[3].id,
                          citations[3].asset.global_annotation(user, False).id)

        # Own global annotation
        self.assertTrue(citations[4].asset.title,
                        "Mediathread: Introduction")
        self.assertEquals(citations[4].id,
                          citations[4].asset.global_annotation(user, False).id)
