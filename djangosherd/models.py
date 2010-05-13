import datetime
import re
import simplejson as json

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.loading import get_model

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from tagging.models import Tag
from tagging.fields import TagField

from structuredcollaboration.models import Collaboration
from django.db.models.signals import post_save

Asset = models.get_model('assetmgr', 'asset')
User = models.get_model('auth', 'user')
Comment = get_model('comments','comment')


NULL_FIELDS = dict((i, None) for i in
                   'range1 range2 title'.split())

ANN_TYPE_CHOICES = ((0,'null'),
                (1,'seconds'),
                (2,'coordinate'),
                )

class Annotation(models.Model):
    #this would simplify is_null handling and also make it possible to give friendly range printing
    #server/template-side
    #wanted: type = models.SmallIntegerField(default=0,choices=ANN_TYPE_CHOICES)
    range1 = models.FloatField(default=None, null=True)
    range2 = models.FloatField(default=None, null=True)
    annotation_data = models.TextField(blank=True, null=True)

    def annotation(self):
        if self.annotation_data:
            return json.loads(self.annotation_data)
        else:
            return None

    def is_null(self):
        return self.range1 is None and self.range2 is None

    def save(self, *args, **kw):
        """
        No intelligence here like setting range2 from range1--the client does this
        """
        return models.Model.save(self, *args, **kw)

    @staticmethod
    def secondsToCode(seconds_float,long_format=False):
        seconds = int(seconds_float)
        #assuming DIV: watchout python3k!
        hrs = seconds/3600 
        mins = (seconds % 3600)/60
        secs = seconds % 60
        rv = "%02d" % secs
        if mins or long_format:
            rv = "%02d:"%mins + rv
        elif not hrs:
            rv = "0:"+rv
        if hrs or long_format:
            rv = "%02d:"%hrs + rv
        return rv

    def range_as_timecode(self):
        tc_range = ""
        if self.range1 is not None:
            tc_range += self.secondsToCode(self.range1)
        if self.range2 is not None \
               and self.range2 != self.range1 :
            tc_range += " - %s" % self.secondsToCode(self.range2)
        return tc_range
    @property
    def dir(self):
        return dir(self)

class SherdNoteManager(models.Manager):

    def global_annotation(self, asset, author):
        """
        for non-clip-like annotations, we'll just use a single annotation per (asset, author)
        and store tags and an annotation body on it.
        """
        global_annotation, created = self.get_or_create(asset=asset, author=author,
                                                        **NULL_FIELDS)
        return global_annotation, created
    @property
    def dir(self):
        return dir(self)
        

    def references_in_string(self,text):
        """
        citation references to sherdnotes
        in the future this might be a db call,
        but for now we regex for links to the annotations
        """
        #"'s to escape openCitation() duplicates
        regex_string = r'(name=|href=|openCitation\()[\'"]/asset/(\d+)/annotations/(\d+)'
        rv = []
        for ann in re.findall(regex_string,text):
            note_id = int(ann[2])
            try:
                note = self.get(pk=note_id)
                
            except self.model.DoesNotExist:
                #title is NON-STANDARD to Annotation base
                note = self.model(id=note_id, 
                                  title="Annotation Deleted",
                                  asset_id=int(ann[1]),
                                  )
            rv.append(note)
        return rv

class SherdNote(Annotation):
    """

    >>> user = User.objects.create(username='lammy')
    >>> asset = Asset.objects.create(title='a lovely asset')
    >>> one = SherdNote.objects.create(author=user, asset=asset)

    >>> one.tags = "foo bar"
    >>> one.tags
    "foo bar"

    >>> one.save()
    >>> sorted(tag.name for tag in get_model('tagging', 'Tag').objects.all())
    [u'bar', u'foo']

    Deleting an annotation should delete all its associated tags:
    >>> one.delete()
    >>> sorted(tag.name for tag in get_model('tagging', 'Tag').objects.all())
    []

    Starting all over ...
    >>> one = SherdNote.objects.create(author=user, asset=asset)
    >>> one.tags = "foo"
    >>> one.save()

    >>> SherdNote.objects.all()
    [<SherdNote: SherdNote object>]

    Deleting an asset should delete all its associated annotations:
    >>> asset.delete()
    >>> SherdNote.objects.all()
    []

    And the tags on those annotations:
    >>> sorted(tag.name for tag in get_model('tagging', 'Tag').objects.all())
    [u'foo']

    (the above should be [] but i don't know why it's wrong)
    
    For a given (user, asset), there can be only one range-less annotation:
    >>> asset = Asset.objects.create(title='a lovely asset')
    >>> one = SherdNote.objects.create(author=user, asset=asset)
    >>> two = SherdNote.objects.create(author=user, asset=asset)
    Traceback (most recent call last):
    ...
    Exception: Only one rangeless annotation may be stored per (user,asset)

    But we can have as many ranged annotations as we want, even if they have the same
    ranges:
    >>> three = SherdNote.objects.create(author=user, asset=asset, range1=0.6)
    >>> four = SherdNote.objects.create(author=user, asset=asset, range1=0.6, range2=2.4)
    >>> five = SherdNote.objects.create(author=user, asset=asset, range1=0.6, range2=2.4)

    For the sake of sanity, ranged annotations with an endpoint and no startpoint
    are not allowed; instead this is fixed up silently on save:
    >>> six = SherdNote.objects.create(author=user, asset=asset, range2=7.5)
    >>> six.range2
    >>> six.range1
    7.5
    """
    objects = SherdNoteManager()

    title = models.CharField(blank=True,max_length=1024, null=True)
    asset = models.ForeignKey(Asset)
    author = models.ForeignKey(User, null=True)
    tags = TagField()

    body = models.TextField(blank=True,db_index=True, null=True)

    added = models.DateTimeField('date created', editable=False)
    modified = models.DateTimeField('date modified', editable=False)

    def tags_split(self):
        "Because |split filter sucks and doesn't break at commas"
        return Tag.objects.get_for_object(self)

    def add_tag(self, tag):
        self.tags = "%s %s" % (self.tags, tag)

    @property
    def content_object(self):
        """Support similar property as Comment model"""
        return self.asset

    def delete(self):
        Tag.objects.get_for_object(self).delete()
        return Annotation.delete(self)

    def get_absolute_url(self):
        if self.is_null():
            return self.asset.get_absolute_url()
        return reverse('annotation-form', None, 
                       (self.asset.pk, self.pk))

    def save(self, *args, **kw):
        """
        Only allow a single rangeless annotation per (user,asset)
        """

        if not self.pk:
            self.added = datetime.datetime.today()
        self.modified = datetime.datetime.today()

        if not self.is_null():
            # anything goes
            return Annotation.save(self, *args, **kw)

        try:
            global_annotation = SherdNote.objects.get(asset=self.asset, author=self.author,
                                                      **NULL_FIELDS)
        except ObjectDoesNotExist:
            return Annotation.save(self, *args, **kw)

        if global_annotation != self:
            raise Exception("Only one rangeless annotation may be stored per (user,asset)")

        return Annotation.save(self, *args, **kw)
        
        
    @property
    def dir(self):
        return dir(self)


class DiscussionIndex(models.Model):
    """table to index discussions to assets and participants
    helpful in answering:
    1. what discussions does a user care about (those they participated in)
    2. what discussions are connected to a particular asset (for asset page)
    3. what new comments should be featured in Clumper
    """
    participant = models.ForeignKey(User, null=True)
    collaboration = models.ForeignKey(Collaboration)

    asset=models.ForeignKey(Asset, null=True, related_name="discussion_references")

    #just for use-case #3
    comment=models.ForeignKey(Comment, null=True)
    modified=models.DateTimeField(auto_now=True) #update on save

    @property
    def content_object(self):
        """Support similar property as Comment model for Clumper"""
        return self.asset or self.collaboration


    def get_absolute_url(self):
        if self.comment and self.comment.threadedcomment:
            return '/discussion/show/%s#comment-%s' % (self.comment.threadedcomment.root_id, 
                                                       self.comment.id)
    @classmethod
    def with_permission(cls, request,query):
        return [di for di in query if di.collaboration.permission_to('read',request) ]

def comment_indexer(sender, instance=None, created=None, **kwargs):
    if not (hasattr(instance,'comment') and
            hasattr(instance,'user') and
            isinstance(getattr(instance,'content_object',None) , Collaboration)
            ): #duck-typing for Comment and ThreadedComment
        return
    sherds = SherdNote.objects.references_in_string(instance.comment)
    di = None
    if not sherds:
        class NoNote:
            asset = None
        sherds = [ NoNote(), ]
    for ann in sherds:
        di,c = DiscussionIndex.objects.get_or_create(
            participant=instance.user,
            collaboration = instance.content_object,
            asset=ann.asset,
            )
        di.comment = instance
        di.save()

    @property
    def dir(self):
        return dir(self)

post_save.connect(comment_indexer)
