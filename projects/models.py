from django.db import models
from django.db.models.loading import get_model
from django.db.models import Q

import datetime
import re

from django.contrib.auth.models import User, Group
from courseaffils.models import Course
from modelversions import version_model

from structuredcollaboration.models import Collaboration

class Project(models.Model):

    title = models.CharField(max_length=1024)

    course = models.ForeignKey(Course)

    #this is actually the LAST UPDATER for version-control purposes
    author = models.ForeignKey(User)

    #should be limited to course members
    #maybe just in the form:
    #http://collingrady.wordpress.com/2008/07/24/useful-form-tricks-in-django/
    participants = models.ManyToManyField(User,
                                          null=True,
                                          blank=True,
                                          related_name = 'projects',
                                          verbose_name = 'Project Collaborators',
                                          )

    only_save_if_changed = True
    only_save_version_if_changed_fields_to_ignore = ['modified','author']


    body = models.TextField(blank=True)

    submitted = models.BooleanField(default=False)
    feedback = models.TextField(blank=True, null=True)

    modified = models.DateTimeField('date modified', editable=False)


    @models.permalink
    def get_absolute_url(self):
        return ('project-workspace', (), {
                'project_id': self.pk,
                })


    def save(self, *args, **kw):
        self.modified = datetime.datetime.today()
        models.Model.save(self, *args, **kw)
        self.participants.add(self.author)

        self.collaboration(sync_group=True)

        models.Model.save(self)

    def status(self):
        """
        The project's status, one of "draft submitted complete".split()
        """
        if self.submitted:
            #if self.feedback is not None:
            #    return u"complete"
            return u"submitted"
        return u"draft"

    @classmethod
    def get_user_projects(cls,user,course):
        #TODO: change to members of project-related group
        return cls.objects.filter(Q(author=user, course=course)
                                  |Q(participants=user, course=course)
                                  ).distinct()

    def is_participant(self,user_or_request):
        user = getattr(user_or_request,'user',user_or_request)
        return (user == self.author
                or user in self.participants.all())

    def citations(self):
        """
        citation references to sherdnotes
        """
        SherdNote = models.get_model('djangosherd','SherdNote')
        return SherdNote.objects.references_in_string(self.body)
            
    @property
    def content_object(self):
        """Support similar property as Comment model"""
        return self

    def attribution(self, participants=None):
        if participants is None:
            participants = list(self.participants.all())
            if self.author not in participants:
                participants.insert(0,self.author)
        return ', '.join([p.get_full_name() or p.username
                for p in participants])

    def __unicode__(self):
        return u'%s <%r> by %s' % (self.title, self.pk, self.attribution())

    def collaboration(self,request=None,sync_group=False):
        col = None
        try:
            col = Collaboration.get_associated_collab(self)
        except Collaboration.DoesNotExist:
            if request is not None:
                col = Collaboration.objects.create(user=self.author,
                                                   title=self.title,
                                                   content_object=self,
                                                   context=request.collaboration_context,
                                                   policy='PrivateEditorsAreOwners',
                                                   )
        if sync_group and col:
            part = self.participants.all()
            if len(part) > 1 or (col.group_id and col.group.user_set.count() > 1):
                colgrp = col.have_group()
                already_grp = set(colgrp.user_set.all())
                for p in part:
                    if p in already_grp:
                        already_grp.discard(p)
                    else:
                        colgrp.user_set.add(p)
                for oldp in already_grp:
                    colgrp.user_set.remove(oldp)
    
        return col
        
    @property
    def dir(self):
        return dir(self)
        
        
        
ProjectVersion = version_model(Project)
