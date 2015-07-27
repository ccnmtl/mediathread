# pylint: disable-msg=E1101
from datetime import datetime, timedelta
import json
import re

from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.query_utils import Q
from tagging.fields import TagField
from tagging.models import Tag, TaggedItem

from mediathread.assetmgr.models import Asset
from mediathread.taxonomy.models import TermRelationship
from structuredcollaboration.models import Collaboration


NULL_FIELDS = dict((i, None) for i in
                   'range1 range2 title'.split())


class Annotation(models.Model):
    range1 = models.FloatField(default=None, null=True)
    range2 = models.FloatField(default=None, null=True)
    annotation_data = models.TextField(blank=True, null=True)

    def annotation(self):
        if self.annotation_data:
            return json.loads(self.annotation_data)
        else:
            return None

    # Null ranges indicate this is a "global annotation"
    # Global annotations are used to store tag & note level data on an item
    def is_global_annotation(self):
        return self.is_null()

    def is_null(self):
        return self.range1 is None and self.range2 is None

    @staticmethod
    def secondsToCode(seconds_float, long_format=False):
        seconds = int(seconds_float)
        # assuming DIV: watchout python3k!
        hrs = seconds / 3600
        mins = (seconds % 3600) / 60
        secs = seconds % 60
        ret_val = "%02d" % secs
        if mins or long_format:
            ret_val = "%02d:" % mins + ret_val
        elif not hrs:
            ret_val = "0:" + ret_val
        if hrs or long_format:
            ret_val = "%02d:" % hrs + ret_val
        return ret_val

    def range_as_timecode(self):
        tc_range = ""
        if self.range1 == 0 and self.range2 == 0:
            return tc_range
        if self.range1 is not None:
            tc_range += self.secondsToCode(self.range1)
        if (self.range2 is not None and
                self.range2 != self.range1):
            tc_range += " - %s" % self.secondsToCode(self.range2)
        return tc_range


class SherdNoteQuerySet(models.query.QuerySet):

    def filter_by_vocabulary(self, vocabulary):
        if vocabulary is None:
            return self

        # OR'd within vocabulary, AND'd across vocabulary
        content_type = ContentType.objects.get_for_model(SherdNote)
        for vocabulary_id in vocabulary:
            items = TermRelationship.objects.filter(
                content_type_id=content_type,
                object_id__in=self.values_list('id', flat=True),
                term__id__in=vocabulary[vocabulary_id],
                term__vocabulary__id=vocabulary_id)
            if items.count() > 0:
                iids = items.values_list('object_id', flat=True)
                self = self.filter(id__in=iids)
            else:
                self = SherdNote.objects.none()  # nothing matched
        return self

    def filter_by_tags(self, tag_string):
        if tag_string is None or len(tag_string) < 1:
            return self

        if not tag_string.endswith(','):
            tag_string += ','

        return TaggedItem.objects.get_union_by_model(self, tag_string)

    def filter_by_date(self, date_range):
        if date_range is None or len(date_range) < 1:
            return self

        tomorrow = datetime.today() + timedelta(1)
        # Tomorrow at midnight
        enddate = datetime(tomorrow.year, tomorrow.month, tomorrow.day)
        if date_range == 'today':
            startdate = enddate + timedelta(-1)
        elif date_range == 'yesterday':
            startdate = enddate + timedelta(-2)
            enddate = enddate + timedelta(-1)
        elif date_range == 'lastweek':
            startdate = enddate + timedelta(-7)

        return self.filter(Q(added__range=[startdate, enddate]) |
                           Q(modified__range=[startdate, enddate]))

    def get_related_notes(self, assets, record_owner, visible_authors=None,
                          all_items_are_visible=False,
                          tag_string=None, modified=None, vocabulary=None):

        # For efficiency purposes, retrieve all related notes
        self = self.filter(asset__in=assets).order_by(
            'asset__id', 'id').select_related()

        if record_owner:
            # only return author's selections
            self = self.exclude(~Q(author=record_owner))

        if visible_authors is not None and len(visible_authors) > 0:
            if not all_items_are_visible:
                # only return notes that are authored by certain people
                self = self.filter(author__id__in=visible_authors)
            else:
                # return everyone's global annotations (item-level) &
                # regular selections authored by certain people
                self = self.filter(Q(author__id__in=visible_authors) |
                                   Q(range1__isnull=True))

        # filter by tag string, date, vocabulary
        self = self.filter_by_tags(tag_string)
        if self.count() > 0:
            self = self.filter_by_date(modified)
        if self.count() > 0:
            self = self.filter_by_vocabulary(vocabulary)
        return self

    def get_related_assets(self):
        asset_ids = self.values_list('asset__id', flat=True)
        return Asset.objects.filter(id__in=asset_ids).distinct()


class SherdNoteManager(models.Manager):
    def __init__(self, fields=None, *args, **kwargs):
        super(SherdNoteManager, self).__init__(*args, **kwargs)
        self._fields = fields

    def get_query_set(self):
        return SherdNoteQuerySet(self.model, self._fields)

    def filter_by_authors(self, author, visible_authors):
        return self.get_query_set().filter_by_authors(author, visible_authors)

    def filter_by_date(self, date_range):
        return self.get_query_set().filter_by_date(date_range)

    def filter_by_tags(self, tag_string):
        return self.get_query_set().filter_by_tags(tag_string)

    def filter_by_vocabulary(self, vocabulary):
        return self.get_query_set().filter_by_vocabulary(vocabulary)

    def get_related_notes(self, assets, record_owner, visible_authors=None,
                          all_items_are_visible=False,
                          tag_string=None, modified=None, vocabulary=None):
        return self.get_query_set().get_related_notes(
            assets, record_owner, visible_authors,
            all_items_are_visible, tag_string, modified, vocabulary)

    def get_related_assets(self):
        return self.get_query_set().get_related_assets()

    def global_annotation(self, asset, author, auto_create=True):
        """
        for non-clip-like annotations, we'll just use a
        single annotation per (asset, author)
        and store tags and an annotation body on it.
        """
        args = NULL_FIELDS.copy()
        args.update(asset=asset, author=author)

        if auto_create:
            return self.get_or_create(**args)
        else:
            try:
                gannotation = self.get(**args)
            except:
                gannotation = None
            return gannotation, False

    def fully_qualify_references(self, text, host):
        """
        Replace relative urls with fully-qualified urls
        Designed for exporting project contents
        """

        # annotations
        regex_string = \
            r'(name=|href=|openCitation\()[\'"]/asset/(\d+)/annotations/(\d+)'
        replace_with = r'href="http://%s/asset/\2/annotations/\3' % host
        text = re.sub(regex_string, replace_with, text)

        # assets
        regex_string = r'(name=|href=|openCitation\()[\'"]/asset/(\d+)/[^a]'
        replace_with = r'href="http://%s/asset/\2/"' % host
        text = re.sub(regex_string, replace_with, text)

        return text

    def references_in_string(self, text, user):
        """
        citation references to sherdnotes
        in the future this might be a db call,
        but for now we regex for links to the annotations
        """
        # "'s to escape openCitation() duplicates
        regex_string = \
            r'(name=|href=|openCitation\()[\'"]/asset/(\d+)/annotations/(\d+)'
        ret_val = []
        for ann in re.findall(regex_string, text):
            note_id = int(ann[2])
            try:
                note = self.get(pk=note_id)

            except self.model.DoesNotExist:
                # title is NON-STANDARD to Annotation base
                note = self.model(id=note_id,
                                  title="Annotation Deleted",
                                  asset_id=int(ann[1]),
                                  )
            ret_val.append(note)

        if user:
            regex_string = \
                r'(name=|href=|openCitation\()[\'"]/asset/(\d+)/[^a]'
            for asset in re.findall(regex_string, text):
                asset_id = int(asset[1])
                try:
                    # get the global annotation for this asset
                    asset = Asset.objects.get(pk=asset_id)
                    note = asset.global_annotation(user, True)
                except Asset.DoesNotExist:
                    # title is NON-STANDARD to Annotation base
                    note = self.model(id=0,
                                      title="Asset Deleted",
                                      asset_id=asset_id)
                ret_val.append(note)

        return ret_val

    def migrate_one(self, old_note, new_asset, user,
                    include_tags, include_notes):
        new_note = None

        if (old_note.is_global_annotation() and
                new_asset.global_annotation(user, False)):
            # A global annotation already exists
            # from this user
            # Return the existing global_annotation
            new_note = new_asset.global_annotation(user, False)
        else:
            try:
                new_note = SherdNote.objects.get(
                    asset=new_asset,
                    range1=old_note.range1,
                    range2=old_note.range2,
                    annotation_data=old_note.annotation_data,
                    title=old_note.title,
                    author=user)
            except SherdNote.DoesNotExist:
                new_note = SherdNote(asset=new_asset,
                                     range1=old_note.range1,
                                     range2=old_note.range2,
                                     annotation_data=old_note.annotation_data,
                                     title=old_note.title,
                                     author=user)

        if include_tags:
            new_note.tags = (new_note.tags or '') + (old_note.tags or '')
        if include_notes:
            new_note.body = (new_note.body or '') + (old_note.body or '')

        new_note.save()
        return new_note


class SherdNote(Annotation):
    objects = SherdNoteManager()

    title = models.CharField(blank=True, max_length=1024, null=True)
    asset = models.ForeignKey(Asset, related_name="sherdnote_set")
    author = models.ForeignKey(User, null=True, blank=True)
    tags = TagField()
    body = models.TextField(blank=True, null=True)
    added = models.DateTimeField('date created', editable=False,
                                 auto_now_add=True)
    modified = models.DateTimeField('date modified', editable=False,
                                    auto_now=True)

    def __unicode__(self):
        username = self.author.username if self.author else ''
        return "[%s] %s for (%s) in (%s)" % (username,
                                             self.title,
                                             self.asset.title,
                                             self.asset.course.title)

    def tags_split(self):
        "Because |split filter sucks and doesn't break at commas"
        return Tag.objects.get_for_object(self)

    def add_tag(self, tag):
        self.tags = "%s,%s" % (self.tags, tag)

    @property
    def content_object(self):
        """Support similar property as Comment model"""
        return self.asset

    def delete(self):
        Tag.objects.update_tags(self, None)
        return Annotation.delete(self)

    def get_absolute_url(self):
        try:
            if self.is_null():
                return self.asset.get_absolute_url()
            return reverse('annotation-view', None,
                           (self.asset.pk, self.pk))
        except:
            return ''

    @classmethod
    def date_filter_for(cls, field):

        def date_filter(note, date_range):
            date = getattr(note, field)
            date = datetime.date(date.year, date.month, date.day)
            today = datetime.date.today()
            if date_range == 'today':
                return date == today
            elif date_range == 'yesterday':
                before_yesterday = today + datetime.timedelta(-2)
                return date > before_yesterday and date < today
            elif date_range == 'lastweek':
                over_a_week_ago = today + datetime.timedelta(-8)
                return date > over_a_week_ago

        return date_filter

    def update_references_in_string(self, text, old_note):
        """
        substitute my new asset.id & id for the old references.
        """
        regex_string = \
            (r'(name=|href=|openCitation\()([\'"]/asset/)(%s)'
             '(/annotations/)(%s)/' % (old_note.asset.id, old_note.id))

        # annotations
        sub = r'\g<1>\g<2>%s\g<4>%s/' % (self.asset.id, self.id)
        return re.sub(regex_string, sub, text)


class DiscussionIndex(models.Model):
    """table to index discussions to assets and participants
    helpful in answering:
    1. what discussions does a user care about (those they participated in)
    2. what discussions are connected to a particular asset (for asset page)
    3. what new comments should be featured in Clumper
    """
    participant = models.ForeignKey(User, null=True)
    collaboration = models.ForeignKey(Collaboration)

    asset = models.ForeignKey(Asset, null=True,
                              related_name="discussion_references")

    # just for use-case #3
    comment = models.ForeignKey(Comment, null=True)
    modified = models.DateTimeField(auto_now=True)  # update on save

    def __unicode__(self):
        return unicode(self.body)

    @property
    def body(self):
        if self.comment:
            parts = re.split('\<\/?[a-zA-Z]+[^>]*>', self.comment.comment)
            return ''.join(parts)
        else:
            return ''

    @property
    def content_object(self):
        """Support similar property as Comment model for Clumper"""
        return self.asset or self.collaboration

    def clump_parent(self, group_by=None):
        if hasattr(self.collaboration.content_object, 'body'):
            return self.collaboration.content_object
        return self.collaboration if group_by == 'discussion' \
            else self.content_object

    def get_parent_url(self):
        if self.comment and self.comment.threadedcomment:
            return '/discussion/%s' % self.comment.threadedcomment.root_id

    def get_absolute_url(self):
        if self.comment and self.comment.threadedcomment:
            return '/discussion/%s#comment-%s' % \
                (self.comment.threadedcomment.root_id, self.comment.id)
        elif self.collaboration.content_object:
            return self.collaboration.content_object.get_absolute_url()

    def get_type_label(self):
        if self.comment and self.comment.threadedcomment:
            return 'discussion'
        elif self.collaboration.content_object:
            return 'project'
        else:
            return ''

    @classmethod
    def with_permission(cls, request, query):
        return [di for di in query
                if di.collaboration.permission_to(
                    'read', request.course, request.user)]

    @classmethod
    def update_class_references(cls, sherdsource, participant, comment,
                                collaboration, author):
        sherds = SherdNote.objects.references_in_string(sherdsource, author)
        if not sherds:
            class NoNote:
                asset = None
            sherds = [NoNote(), ]

        for ann in sherds:
            try:
                disc, created = DiscussionIndex.objects.get_or_create(
                    participant=participant, collaboration=collaboration,
                    asset=ann.asset)
                disc.comment = comment
                disc.save()
            except Asset.DoesNotExist:
                pass  # some annotations or assets may have been deleted
