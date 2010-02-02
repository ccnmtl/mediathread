from django.test import TestCase, Client
import datetime, time

# make some tests!
# test the included policies
# on fake objects/structures
from discussions.models import *
from django.core import serializers
import pdb


from django.contrib.contenttypes.models import ContentType


class DiscussionTestCases(TestCase):
    # for now, installing fixtures manually and overriding the pk for the course contenttype manually.
    # (see bug http://code.djangoproject.com/ticket/7052 )
    
    #fixtures = ["test_data.json"]
    
    def setup(self):
        course_content_type = ContentType.objects.get(model='course').pk
        
        #Got these straight from the Vietnam DB, like so:
        #./manage.py dumpdata --indent=4 courseaffils
        #./manage.py dumpdata --indent=4 structuredcollaboration
        
        data = """[
            {
                "pk": 3, 
                "model": "courseaffils.course", 
                "fields": {
                    "faculty_group": 1, 
                    "group": 55, 
                    "title": "CCNMTL Internal"
                }
            },
            {
                "pk": 2, 
                "model": "structuredcollaboration.collaboration", 
                "fields": {
                    "_order": 2, 
                    "group": 55, 
                    "title": "CCNMTL Internal", 
                    "_policy": null, 
                    "object_pk": "3", 
                    "_parent": null, 
                    "user": null, 
                    "content_type":  %d,
                    "slug": "CCNMTL_Internal"
                }
            }
        ]"""  % course_content_type
        
        for obj in serializers.deserialize("json", data):
            obj.save()
            
    def test_set_and_getcourse(self):
        #pdb.set_trace()
        self.setup()
        ccc =Course.objects.get(pk=3)
        ddd = Discussion()
        ddd.set_course (ccc)
        self.assertEqual(ccc, ddd.get_course())
        
 
    def test_type_of_object_discussed(self):
        self.setup()
        ccc =Course.objects.get(pk=3)
        ddd = Discussion()
        ddd.set_course (ccc)
        self.assertEqual(ddd.type_of_object_discussed(), 'course')
        
    def test_get_all_discussions(self):
        self.setup()
        ccc =Course.objects.get(pk=3)
        d1 = Discussion(title = 'asd')
        d1.set_course (ccc)
        d1.save()
        
        d2 = Discussion(title='fgh')
        d2.set_course (ccc)
        d2.save()
        
        collab = Collaboration.get_associated_collab(ccc)
        relateds = Discussion.objects.filter(collaboration = collab)
        
        assert [i.pk for i in relateds] == [1,2]
        #pdb.set_trace()
        
