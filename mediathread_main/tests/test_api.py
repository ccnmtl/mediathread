# from courseaffils.models import Course
# from mediathread_main import course_details
from tastypie.test import ResourceTestCase


class CourseResourceTest(ResourceTestCase):
    # Use ``fixtures`` & ``urls`` as normal. See Django's ``TestCase``
    # documentation for the gory details.
    fixtures = ['unittest_sample_course.json',
                'unittest_sample_projects.json']

    def assertAssetEquals(self, asset, title, author,
                          primary_type, selection_ids, thumb_url):

        self.assertEquals(asset['title'], title)
        self.assertEquals(asset['author']['full_name'], author)
        self.assertEquals(asset['primary_type'], primary_type)
        self.assertEquals(asset['thumb_url'], thumb_url)

        self.assertEquals(len(asset['selections']), len(selection_ids))

        for idx, s in enumerate(asset['selections']):
            self.assertEquals(int(s['id']), selection_ids[idx])

    def assertProjectEquals(self, project, title, author, selection_ids):
        self.assertEquals(project['title'], title)
        self.assertEquals(project['attribution'], author)

        self.assertEquals(len(project['selections']), len(selection_ids))
        for idx, s in enumerate(project['selections']):
            self.assertEquals(int(s['id']), selection_ids[idx])
