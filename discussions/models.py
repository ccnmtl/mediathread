from django.db import models
from django.db.models import get_model

User = get_model('auth','user')
Group = get_model('auth','group')


#Hm.... don't really need this.
if 1 == 0:
    from django.db.models import Max
    from django.contrib.contenttypes import generic
    from django.contrib.contenttypes.models import ContentType
    from django.core import urlresolvers
    from django.conf import settings
    from structuredcollaboration.models import Collaboration
    from django.utils.translation import ugettext_lazy as _
    from courseaffils.models import Course
    from datetime import datetime
    import pdb

    class Discussion(models.Model):
        """A threaded discussion.
        
        In the database, threadedcomment objects have a "pointer" to a comment object, which in turn points (via content_type_id and object_pk) to a discussion object.
        Contains helper methods to make it easier to manage all this from the template.
        
        
        The collaboration object determines:
            1) what type of object is being discussed
            2) the pk of the object being discussed
            3) access to the discussion (posting, viewing, etc.)
        
        In practice, for now, a course has a certain number of discussions associated with it via its collaboration object.
        
            
        """
        
        if 1 == 0:
            #removing this: if a discussion is affiliated with a course it
            #should just point at an SC which itself points to the course.
            course = models.ForeignKey(Course,null=True)
        
        collaboration = models.ForeignKey(Collaboration,null=True)
        #Permissions - who is part of this discussion?
        
        #title
        title = models.TextField(_('Title'), blank=True)
        
        #Faculty instructions, if applicable:
        instructions =  models.TextField(_('Instructions'), blank=True)
        
        created = models.DateTimeField('date created', editable=False, default=datetime.now)


        def get_course(self):
            course_type = ContentType.objects.get(app_label="courseaffils", model="course")
            return course_type.get_object_for_this_type(pk = self.collaboration.object_pk)

        def set_course(self, course):
            """ set this discussion's collaboration to the course's collaboration"""
            assert isinstance (course, Course)
            if course is None:
                self.collaboration = None
            course_ct =  ContentType.objects.get (name = 'course')
            sc = Collaboration.get_associated_collab(course)
            assert sc is not None
            self.collaboration = sc
            
          
        def set_assignment(self):
            pass
        
        def get_assignment(self):
            pass
        
        def type_of_object_discussed(self):
            """for now, this is simply a "course" or "project", but could be anything you can point an SC at."""
            return self.collaboration.content_type.name
        
        
        #static method:
        def get_all_discussions_of_this_object (arbitrary_object):
            """ all the discussions of this object- look up the object's content type, then look up"""
            pass
        get_all_discussions_of_this_object = staticmethod(get_all_discussions_of_this_object)
        
        @property
        def date_created(self):
            pass
        
        @property
        def date_of_first_post(self):
            pass
        
        @property
        def date_of_most_recent_post(self):
            pass
        
        @property
        def how_many_threads(self):
            """ number of top-level threads"""
            pass

        @property
        def total_post_count(self):
            """ number of top message counts"""
            pass
        
        @property
        def posts_in_the_past_week(self):
            """ number of posts in the past week"""
            pass

        def delete_all_posts(self):
            pass
        

class Discussion():
    pass

        
