# pylint: disable-msg=R0904
# pylint: disable-msg=E1103
import json

from courseaffils.models import Course
from django.core.cache import cache
from django.test.client import RequestFactory
from django.test.testcases import TestCase
from tagging.models import Tag

from mediathread.api import TagResource
from mediathread.djangosherd.models import SherdNote
from mediathread.factories import MediathreadTestMixin, UserFactory, \
    AssetFactory, SherdNoteFactory
from mediathread.main import course_details


class AssetApiTest(MediathreadTestMixin, TestCase):

    def setUp(self):
        self.setup_sample_course()
        self.setup_alternate_course()

        # instructor that sees both Sample Course & Alternate Course
        self.instructor_three = UserFactory(username='instructor_three')
        self.add_as_faculty(self.sample_course, self.instructor_three)
        self.add_as_faculty(self.alt_course, self.instructor_three)

        self.sample_course = Course.objects.get(title='Sample Course')
        self.alt_course = Course.objects.get(title="Alternate Course")

        self.asset1 = AssetFactory.create(
            title="Test Asset 1",
            course=self.sample_course,
            author=self.instructor_one,
            primary_source='image')

        self.student_note = SherdNoteFactory(
            asset=self.asset1, author=self.student_one,
            tags=',student_one_selection',
            body='student one selection note', range1=0, range2=1)
        self.student_ga = SherdNoteFactory(
            asset=self.asset1, author=self.student_one,
            tags=',image, student_one_global,',
            body='student one global note',
            title=None, is_global_annotation=True)
        self.instructor_note = SherdNoteFactory(
            asset=self.asset1, author=self.instructor_one,
            tags=',image, instructor_one_selection,',
            body='instructor one selection note', range1=1, range2=2)
        self.instructor_ga = SherdNoteFactory(
            asset=self.asset1, author=self.instructor_one,
            tags=',image, instructor_one_global,',
            body='instructor one global note',
            title=None, is_global_annotation=True)

        self.asset2 = AssetFactory.create(
            title='Test Asset 2',
            course=self.sample_course,
            author=self.instructor_one,
            primary_source='video')
        self.asset2_instructor_note = SherdNoteFactory(
            asset=self.asset2, author=self.instructor_one,
            tags=',video, instructor_one_selection,',
            body='instructor one selection note', range1=0, range2=1)
        self.asset2_instructor_ga = SherdNoteFactory(
            asset=self.asset2, author=self.instructor_one,
            tags=',video, instructor_one_global,',
            body='instructor one global note',
            title=None, is_global_annotation=True)

    def tearDown(self):
        cache.clear()

    def get_credentials(self):
        return None

    def assertAssetEquals(self, asset, title, author,
                          primary_type, selection_ids):

        self.assertEquals(asset['title'], title)
        self.assertEquals(asset['author']['public_name'], author)
        self.assertEquals(asset['primary_type'], primary_type)

        self.assertEquals(len(asset['annotations']), len(selection_ids))

        for idx, selection in enumerate(asset['annotations']):
            self.assertEquals(int(selection['id']), selection_ids[idx])

    def test_getall_as_student(self):
        self.assertTrue(
            self.client.login(username=self.student_two.username,
                              password="test"))

        url = '/api/asset/?annotations=true'
        response = self.client.get(url, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        the_json = json.loads(response.content)
        objects = the_json['assets']
        self.assertEquals(len(objects), 2)

        selections = [self.student_note.id, self.instructor_note.id]
        self.assertAssetEquals(objects[0], self.asset1.title,
                               'One, Instructor', 'image', selections)
        self.assertFalse('global_annotation' in objects[0])

        self.assertAssetEquals(
            objects[1], self.asset2.title,
            'One, Instructor', 'video', [self.asset2_instructor_note.id])
        self.assertFalse('global_annotation' in objects[1])

    def test_restricted_getall_as_student(self):
        # Set course details to restricted
        self.sample_course.add_detail(course_details.SELECTION_VISIBILITY_KEY,
                                      0)

        self.assertTrue(
            self.client.login(username=self.student_two.username,
                              password="test"))

        url = '/api/asset/?annotations=true'
        response = self.client.get(url, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        the_json = json.loads(response.content)
        objects = the_json['assets']
        self.assertEquals(len(objects), 2)

        selections = [self.instructor_note.id]
        self.assertAssetEquals(objects[0], self.asset1.title,
                               'One, Instructor', 'image', selections)
        self.assertFalse('global_annotation' in objects[0])

        self.assertAssetEquals(
            objects[1], self.asset2.title,
            'One, Instructor', 'video', [self.asset2_instructor_note.id])
        self.assertFalse('global_annotation' in objects[1])

    def test_getall_as_instructor(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password="test"))
        self.switch_course(self.client, self.sample_course)

        url = '/api/asset/?annotations=true'
        response = self.client.get(url, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        the_json = json.loads(response.content)
        objects = the_json['assets']
        self.assertEquals(len(objects), 2)

        match = [x for x in objects if x['id'] == self.asset1.id]
        self.assertEquals(len(match), 1)
        selections = [self.student_note.id, self.instructor_note.id]
        self.assertAssetEquals(match[0], self.asset1.title,
                               'One, Instructor', 'image', selections)
        self.assertFalse('global_annotation' in objects[0])

        match = [x for x in objects if x['id'] == self.asset2.id]
        self.assertEquals(len(match), 1)
        self.assertAssetEquals(
            match[0], self.asset2.title,
            'One, Instructor', 'video', [self.asset2_instructor_note.id])
        self.assertFalse('global_annotation' in objects[1])

    def test_restricted_getall_as_instructor(self):
        # Set course details to restricted
        self.sample_course.add_detail(course_details.SELECTION_VISIBILITY_KEY,
                                      0)
        self.test_getall_as_instructor()

    def test_getstudentlist_as_student_owner(self):
        self.assert_(self.client.login(username=self.student_one.username,
                                       password="test"))

        record_owner = self.student_one.username
        response = self.client.get(
            "/api/asset/user/%s/?annotations=true" % record_owner,
            {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        the_json = json.loads(response.content)
        self.assertEquals(the_json['space_owner']['username'],
                          self.student_one.username)
        self.assertEquals(the_json['space_viewer']['username'],
                          self.student_one.username)
        self.assertTrue(the_json['editable'])
        self.assertFalse(the_json['citable'])
        self.assertFalse(the_json['is_faculty'])
        self.assertEquals(len(the_json['assets']), 1)
        self.assertEquals(len(the_json['assets'][0]['annotations']), 1)

        annotations = the_json['assets'][0]['annotations']
        self.assertEquals(annotations[0]['title'], self.student_note.title)

        # student one's tags
        self.assertEquals(len(annotations[0]['metadata']['tags']), 1)
        self.assertEquals(annotations[0]['metadata']['body'],
                          "student one selection note")

        self.assertTrue('global_annotation' in the_json['assets'][0])
        gla = the_json['assets'][0]['global_annotation']
        self.assertEquals(len(gla['metadata']['tags']), 2)
        self.assertEquals(gla['metadata']['body'],
                          "student one global note")

    def test_restricted_getstudentlist_as_student_owner(self):
        # Set course details to restricted
        self.sample_course.add_detail(course_details.SELECTION_VISIBILITY_KEY,
                                      0)
        self.test_getstudentlist_as_student_owner()

    def test_getstudentlist_as_student_viewer(self):
        self.assert_(self.client.login(username=self.student_two.username,
                                       password="test"))

        record_owner = self.student_one.username
        response = self.client.get(
            "/api/asset/user/%s/?annotations=true" % record_owner,
            {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        the_json = json.loads(response.content)
        self.assertEquals(the_json['space_owner']['username'],
                          self.student_one.username)
        self.assertEquals(the_json['space_viewer']['username'],
                          self.student_two.username)
        self.assertFalse(the_json['editable'])
        self.assertFalse(the_json['citable'])
        self.assertFalse(the_json['is_faculty'])
        self.assertEquals(len(the_json['assets']), 1)
        self.assertEquals(len(the_json['assets'][0]['annotations']), 1)

        annotations = the_json['assets'][0]['annotations']
        self.assertEquals(annotations[0]['title'], self.student_note.title)

        # student two's tags
        self.assertEquals(len(annotations[0]['metadata']['tags']), 1)
        self.assertEquals(annotations[0]['metadata']['body'],
                          "student one selection note")

        self.assertTrue('global_annotation' in the_json['assets'][0])
        gla = the_json['assets'][0]['global_annotation']
        self.assertEquals(len(gla['metadata']['tags']), 2)
        self.assertEquals(gla['metadata']['body'],
                          "student one global note")

    def test_restricted_getstudentlist_as_student_viewer(self):
        self.sample_course.add_detail(course_details.SELECTION_VISIBILITY_KEY,
                                      0)

        self.assert_(self.client.login(username=self.student_two.username,
                                       password="test"))

        record_owner = self.student_one.username
        response = self.client.get(
            "/api/asset/user/%s/?annotations=true" % record_owner,
            {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        the_json = json.loads(response.content)
        self.assertEquals(the_json['space_owner']['username'],
                          self.student_one.username)
        self.assertEquals(the_json['space_viewer']['username'],
                          self.student_two.username)
        self.assertEquals(len(the_json['assets']), 1)
        self.assertEquals(the_json['assets'][0]['annotation_count'], 0)

        ga = the_json['assets'][0]['global_annotation']
        self.assertEquals(ga['author']['username'], 'student_one')

    def test_getstudentlist_as_instructor(self):
        self.assert_(self.client.login(username=self.instructor_one.username,
                                       password="test"))
        self.switch_course(self.client, self.sample_course)

        record_owner = self.student_one.username
        response = self.client.get(
            "/api/asset/user/%s/?annotations=true" % record_owner,
            {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        the_json = json.loads(response.content)
        self.assertEquals(the_json['space_owner']['username'],
                          self.student_one.username)
        self.assertEquals(the_json['space_viewer']['username'],
                          self.instructor_one.username)
        self.assertFalse(the_json['editable'])
        self.assertFalse(the_json['citable'])
        self.assertTrue(the_json['is_faculty'])
        self.assertEquals(len(the_json['assets']), 1)
        self.assertEquals(len(the_json['assets'][0]['annotations']), 1)

        annotations = the_json['assets'][0]['annotations']
        self.assertEquals(annotations[0]['title'], self.student_note.title)

        self.assertEquals(len(annotations[0]['metadata']['tags']), 1)
        self.assertEquals(annotations[0]['metadata']['body'],
                          "student one selection note")

        self.assertTrue('global_annotation' in the_json['assets'][0])
        gla = the_json['assets'][0]['global_annotation']
        self.assertEquals(len(gla['metadata']['tags']), 2)
        self.assertEquals(gla['metadata']['body'],
                          "student one global note")

    def test_restricted_getstudentlist_as_instructor(self):
        # Set course details to restricted
        self.sample_course.add_detail(course_details.SELECTION_VISIBILITY_KEY,
                                      0)
        self.test_getstudentlist_as_instructor()

    def test_getobject_as_student_owner(self):
        self.assertTrue(
            self.client.login(username=self.student_one.username,
                              password="test"))

        response = self.client.get('/api/asset/%s/' % self.asset1.id,
                                   {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = json.loads(response.content)

        selections = [self.instructor_note.id, self.student_note.id]
        asset = the_json['assets'][str(self.asset1.id)]
        self.assertAssetEquals(
            asset,
            self.asset1.title,
            'One, Instructor', 'image', selections)

        self.assertTrue('global_annotation' in asset)
        self.assertEquals(asset['global_annotation']['id'],
                          self.student_ga.id)

    def test_restricted_getobject_as_student_owner(self):
        self.sample_course.add_detail(course_details.SELECTION_VISIBILITY_KEY,
                                      0)
        self.test_getobject_as_student_owner()

    def test_getobject_as_instructor_viewer(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password="test"))
        self.switch_course(self.client, self.sample_course)

        response = self.client.get('/api/asset/%s/' % self.asset1.id,
                                   {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = json.loads(response.content)

        selections = [self.instructor_note.id, self.student_note.id]
        asset = the_json['assets'][str(self.asset1.id)]
        self.assertAssetEquals(
            asset,
            self.asset1.title,
            'One, Instructor', 'image', selections)

        self.assertTrue('global_annotation' in asset)
        self.assertEquals(asset['global_annotation']['id'],
                          self.instructor_ga.id)

    def test_restricted_getobject_as_instructor_viewer(self):
        self.sample_course.add_detail(course_details.SELECTION_VISIBILITY_KEY,
                                      0)
        self.test_getobject_as_instructor_viewer()

    def test_getobject_as_student_viewer(self):
        self.assertTrue(
            self.client.login(username=self.student_two.username,
                              password="test"))

        response = self.client.get('/api/asset/%s/' % self.asset1.id,
                                   {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = json.loads(response.content)

        selections = [self.instructor_note.id, self.student_note.id]
        asset = the_json['assets'][str(self.asset1.id)]
        self.assertAssetEquals(
            asset,
            self.asset1.title,
            'One, Instructor', 'image', selections)

        self.assertFalse('global_annotation' in asset)

    def test_restricted_getobject_as_student_viewer(self):
        # Set course details to restricted
        self.sample_course.add_detail(course_details.SELECTION_VISIBILITY_KEY,
                                      0)

        self.assertTrue(
            self.client.login(username=self.student_two.username,
                              password="test"))

        response = self.client.get('/api/asset/%s/' % self.asset1.id,
                                   {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = json.loads(response.content)

        selections = [self.instructor_note.id]
        asset = the_json['assets'][str(self.asset1.id)]
        self.assertAssetEquals(
            asset,
            self.asset1.title,
            'One, Instructor', 'image', selections)

        self.assertFalse('global_annotation' in asset)

    def test_getobject_as_nonclassmember(self):
        # Student in Alternate Course attempts
        # to retrieve selections from Sample Course
        self.assertTrue(
            self.client.login(username=self.alt_student.username,
                              password="test"))

        # Student One Selection
        response = self.client.get('/api/asset/%s/' % self.asset1,
                                   {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)

    def test_post_list(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password="test"))
        response = self.client.post('/api/asset/', {})
        self.assertEquals(response.status_code, 405)

    def test_put_detail(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password="test"))

        response = self.client.put('/api/asset/{}/'.format(self.asset2.id),
                                   {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 405)

    def test_delete(self):
        self.assertTrue(
            self.client.login(username=self.instructor_one.username,
                              password="test"))

        response = self.client.delete('/api/asset/{}/'.format(self.asset2.id),
                                      {},
                                      HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 405)

    def test_getobject_multiple_class_member_nocourse(self):
        self.assertTrue(
            self.client.login(username=self.instructor_three.username,
                              password="test"))

        # No course selection yet
        response = self.client.get('/api/asset/%s/' % self.asset1.id, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name,
                          "courseaffils/course_list.html")

    def test_getobject_multiple_class_member_wrongcourse(self):
        self.assertTrue(
            self.client.login(username=self.instructor_three.username,
                              password="test"))
        self.switch_course(self.client, self.alt_course)

        response = self.client.get('/api/asset/%s/' % self.asset1.id,
                                   {}, follow=True,
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name,
                          "assetmgr/asset_not_found.html")

    def test_getobject_multiple_class_member_rightcourse(self):
        self.assertTrue(
            self.client.login(username=self.instructor_three.username,
                              password="test"))

        self.switch_course(self.client, self.sample_course)

        response = self.client.get('/api/asset/%s/' % self.asset1.id, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = json.loads(response.content)

        selections = [self.instructor_note.id, self.student_note.id]
        asset = the_json['assets'][str(self.asset1.id)]
        self.assertAssetEquals(asset, self.asset1.title,
                               'One, Instructor', 'image', selections)

        self.assertFalse('global_annotation' in asset)

    def test_getlist_multiple_class_member(self):
        self.assertTrue(
            self.client.login(username=self.instructor_three.username,
                              password="test"))

        # No course selected
        response = self.client.get('/api/asset/', {})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name,
                          "courseaffils/course_list.html")

        # No dice, login to Alternate Course
        self.switch_course(self.client, self.alt_course)

        # Let's try this again -- asset list
        response = self.client.get('/api/asset/?annotations=true',
                                   {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        the_json = json.loads(response.content)
        objects = the_json['assets']
        self.assertEquals(len(objects), 0)

    def test_render_tag_list(self):
        tags = Tag.objects.usage_for_queryset(self.asset1.sherdnote_set.all(),
                                              counts=True)
        resource = TagResource()
        lst = resource.render_list(None, tags)
        self.assertEquals(len(lst), 5)

        self.assertEquals(lst[0]['count'], 3)
        self.assertEquals(lst[0]['last'], False)
        self.assertEquals(lst[0]['name'], 'image')

        self.assertEquals(lst[1]['count'], 1)
        self.assertEquals(lst[1]['last'], False)
        self.assertEquals(lst[1]['name'], 'instructor_one_global')

        self.assertEquals(lst[2]['count'], 1)
        self.assertEquals(lst[2]['last'], False)
        self.assertEquals(lst[2]['name'], 'instructor_one_selection')

        self.assertEquals(lst[3]['count'], 1)
        self.assertEquals(lst[3]['last'], False)
        self.assertEquals(lst[3]['name'], 'student_one_global')

        self.assertEquals(lst[4]['count'], 1)
        self.assertEquals(lst[4]['last'], True)
        self.assertEquals(lst[4]['name'], 'student_one_selection')

    def test_render_related_tag_list(self):
        request = RequestFactory().get('')
        request.course = self.sample_course

        notes = SherdNote.objects.filter(author=self.student_one)
        lst = TagResource().render_related(request, notes)
        self.assertEquals(len(lst), 3)

        self.assertEquals(lst[0]['count'], 1)
        self.assertEquals(lst[0]['last'], False)
        self.assertEquals(lst[0]['name'], 'image')

        self.assertEquals(lst[1]['count'], 1)
        self.assertEquals(lst[1]['last'], False)
        self.assertEquals(lst[1]['name'], 'student_one_global')

        self.assertEquals(lst[2]['count'], 1)
        self.assertEquals(lst[2]['last'], True)
        self.assertEquals(lst[2]['name'], 'student_one_selection')

    def test_render_tag_list_for_course(self):
        request = RequestFactory().get('')
        request.course = self.sample_course

        notes = SherdNote.objects.filter(author=self.student_one)
        lst = TagResource().render_for_course(request, notes)
        self.assertEquals(len(lst), 6)

        self.assertEquals(lst[0]['count'], 1)
        self.assertEquals(lst[0]['last'], False)
        self.assertEquals(lst[0]['name'], 'image')

        self.assertEquals(lst[1]['count'], 0)
        self.assertEquals(lst[1]['last'], False)
        self.assertEquals(lst[1]['name'], 'instructor_one_global')

        self.assertEquals(lst[2]['count'], 0)
        self.assertEquals(lst[2]['last'], False)
        self.assertEquals(lst[2]['name'], 'instructor_one_selection')

        self.assertEquals(lst[3]['count'], 1)
        self.assertEquals(lst[3]['last'], False)
        self.assertEquals(lst[3]['name'], 'student_one_global')

        self.assertEquals(lst[4]['count'], 1)
        self.assertEquals(lst[4]['last'], False)
        self.assertEquals(lst[4]['name'], 'student_one_selection')

        self.assertEquals(lst[5]['count'], 0)
        self.assertEquals(lst[5]['last'], True)
        self.assertEquals(lst[5]['name'], 'video')

    def test_filter_by_media_type(self):
        self.assertTrue(
            self.client.login(username=self.student_two.username,
                              password="test"))

        url = '/api/asset/?media_type=image'
        response = self.client.get(url)
        the_json = json.loads(response.content)
        objects = the_json['assets']
        self.assertEqual(len(objects), 1)
        self.assertEqual(objects[0]['primary_type'], 'image')

        url = '/api/asset/?media_type=test'
        response = self.client.get(url)
        the_json = json.loads(response.content)
        objects = the_json['assets']
        self.assertEqual(len(objects), 0)

        url = '/api/asset/?media_type=video'
        response = self.client.get(url)
        the_json = json.loads(response.content)
        objects = the_json['assets']
        self.assertEqual(len(objects), 1)
        self.assertEqual(objects[0]['primary_type'], 'video')

        url = '/api/asset/?media_type=all'
        response = self.client.get(url)
        the_json = json.loads(response.content)
        objects = the_json['assets']
        self.assertEqual(len(objects), 2)

        url = '/api/asset/?media_type='
        response = self.client.get(url)
        the_json = json.loads(response.content)
        objects = the_json['assets']
        self.assertEqual(len(objects), 2)

        url = '/api/asset/'
        response = self.client.get(url)
        the_json = json.loads(response.content)
        objects = the_json['assets']
        self.assertEqual(len(objects), 2)

    def test_order_by(self):
        self.assertTrue(
            self.client.login(
                username=self.student_one.username,
                password='test'))

        asset1 = AssetFactory.create(
            title='abcde',
            course=self.sample_course,
            author=self.student_one,
            primary_source='image')
        SherdNoteFactory(
            asset=asset1, author=self.student_one)

        asset2 = AssetFactory.create(
            title='zebra',
            course=self.sample_course,
            author=self.student_one,
            primary_source='image')
        SherdNoteFactory(
            asset=asset2, author=self.student_one)

        asset3 = AssetFactory.create(
            title='maurice',
            course=self.sample_course,
            author=self.instructor_one,
            primary_source='image')
        SherdNoteFactory(
            asset=asset3, author=self.student_one)

        asset4 = AssetFactory.create(
            title='ZZzzzzz',
            course=self.sample_course,
            author=self.student_one,
            primary_source='image')
        SherdNoteFactory(
            asset=asset4, author=self.student_one)

        # Make 50 more items in this course to trigger pagination
        for i in range(50):
            asset = AssetFactory.create(
                title='item {}'.format(i),
                course=self.sample_course,
                author=self.student_one,
                primary_source='image')
            SherdNoteFactory(
                asset=asset, author=self.student_one)

        url = '/api/asset/?order_by=title'
        response = self.client.get(url)
        the_json = json.loads(response.content)
        self.assertEqual(the_json.get('asset_count'), 56)
        objects = the_json['assets']
        self.assertEqual(len(objects), 20)
        self.assertEqual(objects[0]['primary_type'], 'image')
        self.assertEqual(objects[0]['title'], 'abcde')
        self.assertEqual(objects[10]['title'], 'item 17')
        self.assertEqual(objects[19]['title'], 'item 25')

        url = '/api/asset/?order_by=-title'
        response = self.client.get(url)
        the_json = json.loads(response.content)
        self.assertEqual(the_json.get('asset_count'), 56)
        objects = the_json['assets']
        self.assertEqual(len(objects), 20)
        self.assertEqual(objects[0]['title'], 'ZZzzzzz')
        self.assertEqual(objects[0]['primary_type'], 'image')
        self.assertEqual(objects[19]['title'], 'item 40')

        url = '/api/asset/?order_by=author'
        response = self.client.get(url)
        the_json = json.loads(response.content)
        self.assertEqual(the_json.get('asset_count'), 56)
        objects = the_json['assets']
        self.assertEqual(len(objects), 20)
        self.assertEqual(objects[0]['primary_type'], 'image')

        url = '/api/asset/?order_by=-author'
        response = self.client.get(url)
        the_json = json.loads(response.content)
        self.assertEqual(the_json.get('asset_count'), 56)
        objects = the_json['assets']
        self.assertEqual(len(objects), 20)
        self.assertEqual(objects[0]['primary_type'], 'image')
