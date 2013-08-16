from courseaffils.models import Course
from mediathread.main import course_details
from tastypie.test import ResourceTestCase


class SherdNoteResourceTest(ResourceTestCase):
    # Use ``fixtures`` & ``urls`` as normal. See Django's ``TestCase``
    # documentation for the gory details.
    fixtures = ['unittest_sample_course.json']

    def assertNoteEquals(self, note, aid, title, author, is_global_annotation):
        self.assertEquals(note['asset_id'], aid)
        self.assertEquals(note['title'], title)
        self.assertEquals(note['author']['public_name'], author)
        self.assertEquals(note['is_global_annotation'], is_global_annotation)

    def test_student_getlist(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        response = self.api_client.get('/_main/api/v1/sherdnote/',
                                       format='json')
        self.assertValidJSONResponse(response)

        json = self.deserialize(response)
        objects = json['objects']
        self.assertEquals(len(objects), 9)

        self.assertNoteEquals(objects[0], '1', 'Manage Sources',
                              'Instructor One', False)

        self.assertNoteEquals(objects[1], '1', 'Annotations',
                              'Instructor One', False)

        self.assertNoteEquals(objects[2], '2', 'Our esteemed leaders',
                              'Instructor One', False)

        self.assertNoteEquals(objects[3], '3', 'Left Corner',
                              'Instructor One', False)

        self.assertNoteEquals(objects[4], '2', 'The Award',
                              'Student One', False)

        self.assertNoteEquals(objects[5], '2', None,
                              'Student One', True)

        self.assertNoteEquals(objects[6], '2', 'Nice Tie',
                              'Student Two', False)

        self.assertNoteEquals(objects[7], '1', 'Whole Item Selection',
                              'Instructor One', False)

        self.assertNoteEquals(objects[8], '1',
                              'Video Selection Is Time-based',
                              'test_instructor_two', False)

        self.client.logout()

    def test_student_getlist_restricted(self):
        # Set course details to restricted
        sample_course = Course.objects.get(title="Sample Course")
        sample_course.add_detail(course_details.SELECTION_VISIBILITY_KEY, 0)

        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        response = self.api_client.get('/_main/api/v1/sherdnote/',
                                       format='json')
        self.assertValidJSONResponse(response)

        json = self.deserialize(response)
        objects = json['objects']
        self.assertEquals(len(objects), 8)

        self.assertNoteEquals(objects[0], '1', 'Manage Sources',
                              'Instructor One', False)

        self.assertNoteEquals(objects[1], '1', 'Annotations',
                              'Instructor One', False)

        self.assertNoteEquals(objects[2], '2', 'Our esteemed leaders',
                              'Instructor One', False)

        self.assertNoteEquals(objects[3], '3', 'Left Corner',
                              'Instructor One', False)

        self.assertNoteEquals(objects[4], '2', 'The Award',
                              'Student One', False)

        self.assertNoteEquals(objects[5], '2', None, 'Student One', True)

        self.assertNoteEquals(objects[6], '1', 'Whole Item Selection',
                              'Instructor One', False)

        self.assertNoteEquals(objects[7], '1',
                              'Video Selection Is Time-based',
                              'test_instructor_two', False)

        self.client.logout()

    def test_student_getlist_filteredbyauthor(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        response = self.api_client.get(
            '/_main/api/v1/sherdnote/?author__id=4',
            format='json')
        self.assertValidJSONResponse(response)

        json = self.deserialize(response)
        objects = json['objects']
        self.assertEquals(len(objects), 1)

        self.assertNoteEquals(objects[0], '2', 'Nice Tie',
                              'Student Two', False)

        self.client.logout()

    def test_student_getlist_restricted_filteredbyauthor(self):
        # Set course details to restricted
        sample_course = Course.objects.get(title="Sample Course")
        sample_course.add_detail(course_details.SELECTION_VISIBILITY_KEY, 0)

        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        response = self.api_client.get(
            '/_main/api/v1/sherdnote/?author__id=4',
            format='json')
        self.assertValidJSONResponse(response)

        json = self.deserialize(response)
        objects = json['objects']
        self.assertEquals(len(objects), 0)
        self.client.logout()

    def test_student_getobject(self):
        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        # Own Selection
        response = self.api_client.get('/_main/api/v1/sherdnote/8/',
                                       format='json')
        self.assertValidJSONResponse(response)
        json = self.deserialize(response)
        self.assertNoteEquals(json, '2', 'The Award', 'Student One', False)

        # Own Global Annotation
        response = self.api_client.get('/_main/api/v1/sherdnote/9/',
                                       format='json')
        self.assertValidJSONResponse(response)
        json = self.deserialize(response)
        self.assertNoteEquals(json, '2', None, 'Student One', True)

        # Instructor Selection
        response = self.api_client.get('/_main/api/v1/sherdnote/5/',
                                       format='json')
        self.assertValidJSONResponse(response)
        json = self.deserialize(response)
        self.assertNoteEquals(json, '2', 'Our esteemed leaders',
                              'Instructor One', False)

        # Instructor's Global Annotation
        response = self.api_client.get('/_main/api/v1/sherdnote/4/',
                                       format='json')
        self.assertEqual(response.status_code, 404)

        # Peer Selection
        response = self.api_client.get('/_main/api/v1/sherdnote/10/',
                                       format='json')
        self.assertValidJSONResponse(response)
        json = self.deserialize(response)
        self.assertNoteEquals(json, '2', 'Nice Tie', 'Student Two', False)

        # Peer Global Annotation
        response = self.api_client.get('/_main/api/v1/sherdnote/11/',
                                       format='json')
        self.assertEqual(response.status_code, 404)

    def test_student_getobject_restricted(self):
        # Set course details to restricted
        sample_course = Course.objects.get(title="Sample Course")
        sample_course.add_detail(course_details.SELECTION_VISIBILITY_KEY, 0)

        self.assertTrue(
            self.api_client.client.login(username="test_student_one",
                                         password="test"))

        # Own Selection
        response = self.api_client.get('/_main/api/v1/sherdnote/8/',
                                       format='json')
        self.assertValidJSONResponse(response)
        json = self.deserialize(response)
        self.assertNoteEquals(json, '2', 'The Award', 'Student One', False)

        # Own Global Annotation
        response = self.api_client.get('/_main/api/v1/sherdnote/9/',
                                       format='json')
        self.assertValidJSONResponse(response)
        json = self.deserialize(response)
        self.assertNoteEquals(json, '2', None, 'Student One', True)

        # Instructor Selection
        response = self.api_client.get('/_main/api/v1/sherdnote/5/',
                                       format='json')
        self.assertValidJSONResponse(response)
        json = self.deserialize(response)
        self.assertNoteEquals(json, '2', 'Our esteemed leaders',
                              'Instructor One', False)

        # Instructor's Global Annotation
        response = self.api_client.get('/_main/api/v1/sherdnote/4/',
                                       format='json')
        self.assertEqual(response.status_code, 404)

        # Peer Selection
        response = self.api_client.get('/_main/api/v1/sherdnote/10/',
                                       format='json')
        self.assertEqual(response.status_code, 404)

        # Peer Global Annotation
        response = self.api_client.get('/_main/api/v1/sherdnote/11/',
                                       format='json')
        self.assertEqual(response.status_code, 404)

    def test_instructor_getlist(self):
        self.assertTrue(self.api_client.client.login(
            username="test_instructor", password="test"))

        response = self.api_client.get('/_main/api/v1/sherdnote/',
                                       format='json')
        self.assertValidJSONResponse(response)

        json = self.deserialize(response)
        objects = json['objects']
        self.assertEquals(len(objects), 11)

        self.assertNoteEquals(objects[0], '1', None,
                              'Instructor One', True)

        self.assertNoteEquals(objects[1], '1', 'Manage Sources',
                              'Instructor One', False)

        self.assertNoteEquals(objects[2], '1', 'Annotations',
                              'Instructor One', False)

        self.assertNoteEquals(objects[3], '2', None,
                              'Instructor One', True)

        self.assertNoteEquals(objects[4], '2', 'Our esteemed leaders',
                              'Instructor One', False)

        self.assertNoteEquals(objects[5], '3', None,
                              'Instructor One', True)

        self.assertNoteEquals(objects[6], '3', 'Left Corner',
                              'Instructor One', False)

        self.assertNoteEquals(objects[7], '2', 'The Award',
                              'Student One', False)

        self.assertNoteEquals(objects[8], '2', 'Nice Tie',
                              'Student Two', False)

        self.assertNoteEquals(objects[9], '1', 'Whole Item Selection',
                              'Instructor One', False)

        self.assertNoteEquals(objects[10], '1',
                              'Video Selection Is Time-based',
                              'test_instructor_two', False)

        self.client.logout()

    def test_instructor_getlist_restricted(self):
        # Set course details to restricted
        sample_course = Course.objects.get(title="Sample Course")
        sample_course.add_detail(course_details.SELECTION_VISIBILITY_KEY, 0)

        self.test_instructor_getlist()

    def test_instructor_getobject(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        # Student One Selection
        response = self.api_client.get('/_main/api/v1/sherdnote/8/',
                                       format='json')
        self.assertValidJSONResponse(response)
        json = self.deserialize(response)
        self.assertNoteEquals(json, '2', 'The Award', 'Student One', False)

        # Student One Global Annotation
        response = self.api_client.get('/_main/api/v1/sherdnote/9/',
                                       format='json')
        self.assertEqual(response.status_code, 404)

        # Instructor Selection
        response = self.api_client.get('/_main/api/v1/sherdnote/5/',
                                       format='json')
        self.assertValidJSONResponse(response)
        json = self.deserialize(response)
        self.assertNoteEquals(json, '2', 'Our esteemed leaders',
                              'Instructor One', False)

        # Instructor's Global Annotation
        response = self.api_client.get('/_main/api/v1/sherdnote/4/',
                                       format='json')
        self.assertValidJSONResponse(response)
        json = self.deserialize(response)
        self.assertNoteEquals(json, '2', None, 'Instructor One', True)

        # Peer Selection
        response = self.api_client.get('/_main/api/v1/sherdnote/10/',
                                       format='json')
        self.assertValidJSONResponse(response)
        json = self.deserialize(response)
        self.assertNoteEquals(json, '2', 'Nice Tie', 'Student Two', False)

        # Peer Global Annotation
        response = self.api_client.get('/_main/api/v1/sherdnote/11/',
                                       format='json')
        self.assertEqual(response.status_code, 404)

    def test_instructor_getobject_restricted(self):
        # Set course details to restricted
        sample_course = Course.objects.get(title="Sample Course")
        sample_course.add_detail(course_details.SELECTION_VISIBILITY_KEY, 0)

        self.test_instructor_getobject()

    def test_nonclassmember_getobject(self):
        # Student in Alternate Course attempts
        # to retrieve selections from Sample Course
        self.assertTrue(
            self.api_client.client.login(username="test_student_alt",
                                         password="test"))

        # Student One Selection
        response = self.api_client.get('/_main/api/v1/sherdnote/8/',
                                       format='json')
        self.assertEqual(response.status_code, 404)

        # Student One Global Annotation
        response = self.api_client.get('/_main/api/v1/sherdnote/9/',
                                       format='json')
        self.assertEqual(response.status_code, 404)

        # Instructor Selection
        response = self.api_client.get('/_main/api/v1/sherdnote/5/',
                                       format='json')
        self.assertEqual(response.status_code, 404)

        # Instructor's Global Annotation
        response = self.api_client.get('/_main/api/v1/sherdnote/4/',
                                       format='json')
        self.assertEqual(response.status_code, 404)

        # Instructor in Alternate Course attempts
        # to retrieve selections from Sample Course
        self.assertTrue(
            self.api_client.client.login(username="test_instructor_alt",
                                         password="test"))

        # Student One Selection
        response = self.api_client.get('/_main/api/v1/sherdnote/8/',
                                       format='json')
        self.assertEqual(response.status_code, 404)

        # Student One Global Annotation
        response = self.api_client.get('/_main/api/v1/sherdnote/9/',
                                       format='json')
        self.assertEqual(response.status_code, 404)

        # Instructor Selection
        response = self.api_client.get('/_main/api/v1/sherdnote/5/',
                                       format='json')
        self.assertEqual(response.status_code, 404)

        # Instructor's Global Annotation
        response = self.api_client.get('/_main/api/v1/sherdnote/4/',
                                       format='json')
        self.assertEqual(response.status_code, 404)

    def test_post_list(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        self.assertHttpMethodNotAllowed(self.api_client.post(
            '/_main/api/v1/sherdnote/', format='json', data={}))

    def test_put_detail(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        self.assertHttpMethodNotAllowed(self.api_client.put(
            '/_main/api/v1/sherdnote/2/', format='json', data={}))

    def test_delete(self):
        self.assertTrue(
            self.api_client.client.login(username="test_instructor",
                                         password="test"))

        self.assertHttpMethodNotAllowed(self.api_client.delete(
            '/_main/api/v1/sherdnote/2/', format='json'))

    def test_getobject_multiple_class_member(self):
        # User prompted to select class after login
        # User can access notes for this class
        # User cannot access notes for another class
        self.assertTrue(
            self.api_client.client.login(username="test_student_three",
                                         password="test"))

        # Student One Selection from Sample Course
        response = self.api_client.get('/_main/api/v1/sherdnote/8/',
                                       format='json')
        self.assertHttpOK(response)
        self.assertEquals(response.template[0].name,
                          "courseaffils/select_course.html")

        # No dice, login to Alternate Course
        response = self.api_client.client.get(
            '/?set_course=Alternate%20Course%20Members&next=/', follow=True)
        self.assertHttpOK(response)
        self.assertEquals(response.template[0].name, "homepage.html")

        # Let's try this again --
        # Student One Public Selection from Sample Course
        response = self.api_client.get('/_main/api/v1/sherdnote/9/',
                                       format='json')
        self.assertEqual(response.status_code, 404)

        response = self.api_client.get('/_main/api/v1/sherdnote/8/',
                                       format='json')
        self.assertValidJSONResponse(response)
        json = self.deserialize(response)
        self.assertNoteEquals(json, '2', 'The Award', 'Student One', False)

        # Now ask for one from Alternate Course
        response = self.api_client.get('/_main/api/v1/sherdnote/15/',
                                       format='json')
        self.assertValidJSONResponse(response)
        json = self.deserialize(response)
        self.assertNoteEquals(json, '4', 'Whole Item Selection',
                              'test_student_three', False)

    def test_getlist_multiple_class_member(self):
        # User prompted to login to class after login
        # User receives only assets for logged-in class
                # User prompted to select class after login
        # User can access notes for this class
        # User cannot access notes for another class
        self.assertTrue(
            self.api_client.client.login(username="test_student_three",
                                         password="test"))

        # Student One Selection from Sample Course
        response = self.api_client.get('/_main/api/v1/sherdnote/',
                                       format='json')
        self.assertHttpOK(response)
        self.assertEquals(response.template[0].name,
                          "courseaffils/select_course.html")

        # No dice, login to Alternate Course
        response = self.api_client.client.get(
            '/?set_course=Alternate%20Course%20Members&next=/', follow=True)
        self.assertHttpOK(response)
        self.assertEquals(response.template[0].name, "homepage.html")

        # Let's try this again -- asset list please
        response = self.api_client.get('/_main/api/v1/sherdnote/',
                                       format='json')

        json = self.deserialize(response)
        objects = json['objects']
        self.assertEquals(len(objects), 12)

        self.assertNoteEquals(objects[0], '1', 'Manage Sources',
                              'Instructor One', False)

        self.assertNoteEquals(objects[1], '1', 'Annotations',
                              'Instructor One', False)

        self.assertNoteEquals(objects[2], '2', 'Our esteemed leaders',
                              'Instructor One', False)

        self.assertNoteEquals(objects[3], '3', 'Left Corner',
                              'Instructor One', False)

        self.assertNoteEquals(objects[4], '2', 'The Award',
                              'Student One', False)

        self.assertNoteEquals(objects[5], '2', 'Nice Tie',
                              'Student Two', False)

        self.assertNoteEquals(objects[6], '4', 'Research and Evaluation',
                              'test_instructor_alt', False)

        self.assertNoteEquals(objects[7], '4', 'Curricular Context',
                              'test_instructor_alt', False)

        self.assertNoteEquals(objects[8], '4', 'Whole Item Selection',
                              'test_student_three', False)

        self.assertNoteEquals(objects[9], '4', None,
                              'test_student_three', True)

        self.assertNoteEquals(objects[10], '1', 'Whole Item Selection',
                              'Instructor One', False)

        self.assertNoteEquals(objects[11], '1',
                              'Video Selection Is Time-based',
                              'test_instructor_two', False)
