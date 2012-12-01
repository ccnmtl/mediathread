import datetime
from django.contrib.auth.models import User
from tastypie.test import ResourceTestCase
from djangosherd.models import SherdNote

class SherdNoteResourceTest(ResourceTestCase):
    # Use ``fixtures`` & ``urls`` as normal. See Django's ``TestCase``
    # documentation for the gory details.
    fixtures = ['unittest_sample_course.json']
    
    def setUp(self):
        super(SherdNoteResourceTest, self).setUp()
        
    def test_as_student(self):
        # As Course Student
        self.assertTrue(self.api_client.client.login(username="test_student_one", password="test"))
         
        response = self.api_client.get('/_main/api/v1/sherdnote/', format='json')
        self.assertValidJSONResponse(response)
        
        json = self.deserialize(response)
        self.assertEquals(len(json['objects']), 11)
        
        self.client.logout()
        
    def test_as_instructor(self):
        # As Course Student
        self.assertTrue(self.api_client.client.login(username="test_instructor", password="test"))
         
        response = self.api_client.get('/_main/api/v1/sherdnote/', format='json')
        self.assertValidJSONResponse(response)
        
        json = self.deserialize(response)
        self.assertEquals(len(json['objects']), 11)
        
        for note in json['objects']:
            # global annotations have no range and must be attributed to this author
            print note['author']
        
        self.client.logout()
'''        
    def test_public_selections_as_random_student(self):    
        self.assertTrue(self.client.login("test_student_three", "test"))
        
        resp = self.api_client.get('/api/v1/sherdnote/', format='json')
        self.assertValidJSONResponse(resp)
        
        self.client.logout()

    def test_public_selections_as_random_instructor(self):    
        self.assertTrue(self.client.login("test_student_three", "test"))
        
        resp = self.api_client.get('/api/v1/sherdnote/', format='json')
        self.assertValidJSONResponse(resp)
        
        self.client.logout()
        
    def test_get_list_private_selections(self):
        # As Course Student
        
        # As Course Instructor
        
        # As Non-Course Student
        
        # As Non-Course Instructor 
      
    

    def test_get_list_json(self):
        resp = self.api_client.get('/api/v1/entries/', format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)

        # Scope out the data for correctness.
        self.assertEqual(len(self.deserialize(resp)['objects']), 12)
        # Here, we're checking an entire structure for the expected data.
        self.assertEqual(self.deserialize(resp)['objects'][0], {
            'pk': str(self.entry_1.pk),
            'user': '/api/v1/user/{0}/'.format(self.user.pk),
            'title': 'First post',
            'slug': 'first-post',
            'created': '2012-05-01T19:13:42',
            'resource_uri': '/api/v1/entry/{0}/'.format(self.entry_1.pk)
        })

    def test_get_list_xml(self):
        self.assertValidXMLResponse(self.api_client.get('/api/v1/entries/', format='xml', authentication=self.get_credentials()))

    def test_get_detail_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.get(self.detail_url, format='json'))

    def test_get_detail_json(self):
        resp = self.api_client.get(self.detail_url, format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)

        # We use ``assertKeys`` here to just verify the keys, not all the data.
        self.assertKeys(self.deserialize(resp), ['created', 'slug', 'title', 'user'])
        self.assertEqual(self.deserialize(resp)['name'], 'First post')

    def test_get_detail_xml(self):
        self.assertValidXMLResponse(self.api_client.get(self.detail_url, format='xml', authentication=self.get_credentials()))

    def test_post_list_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.post('/api/v1/entries/', format='json', data=self.post_data))

    def test_post_list(self):
        # Check how many are there first.
        self.assertEqual(Entry.objects.count(), 5)
        self.assertHttpCreated(self.api_client.post('/api/v1/entries/', format='json', data=self.post_data, authentication=self.get_credentials()))
        # Verify a new one has been added.
        self.assertEqual(Entry.objects.count(), 6)

    def test_put_detail_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.put(self.detail_url, format='json', data={}))

    def test_put_detail(self):
        # Grab the current data & modify it slightly.
        original_data = self.deserialize(self.api_client.get(self.detail_url, format='json', authentication=self.get_credentials()))
        new_data = original_data.copy()
        new_data['title'] = 'Updated: First Post'
        new_data['created'] = '2012-05-01T20:06:12'

        self.assertEqual(Entry.objects.count(), 5)
        self.assertHttpAccepted(self.api_client.put(self.detail_url, format='json', data=new_data, authentication=self.get_credentials()))
        # Make sure the count hasn't changed & we did an update.
        self.assertEqual(Entry.objects.count(), 5)
        # Check for updated data.
        self.assertEqual(Entry.objects.get(pk=25).title, 'Updated: First Post')
        self.assertEqual(Entry.objects.get(pk=25).slug, 'first-post')
        self.assertEqual(Entry.objects.get(pk=25).created, datetime.datetime(2012, 3, 1, 13, 6, 12))

    def test_delete_detail_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.delete(self.detail_url, format='json'))

    def test_delete_detail(self):
        self.assertEqual(Entry.objects.count(), 5)
        self.assertHttpAccepted(self.api_client.delete(self.detail_url, format='json', authentication=self.get_credentials()))
        self.assertEqual(Entry.objects.count(), 4)
'''        