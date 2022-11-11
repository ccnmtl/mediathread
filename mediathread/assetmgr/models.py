from __future__ import unicode_literals

import json
import re
from functools import reduce

from courseaffils.models import Course
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.urls import reverse
from django.db import models
from django.utils.encoding import smart_text
from tagging.models import Tag

from mediathread.assetmgr.custom_storage import private_storage
from mediathread.assetmgr.utils import get_signed_s3_url


METADATA_ORIGINAL_OWNER = 'Original Owner'


class AssetManager(models.Manager):

    def get_by_args(self, args, **constraints):
        """Given some parameters, get an Asset.

        args is typically request.GET.

        Returns the tuple: (success, asset), where success is a
        boolean.
        """
        criteria = Asset.good_args(args)
        if not criteria:
            return (False, None)

        # A simple for loop may be more readable than this reduce():
        # https://stackoverflow.com/a/13638960/173630
        qry = reduce(lambda x, y: x | y,  # composable Q's
                     [models.Q(label=k, url=args[k], primary=True)
                      for k in criteria])
        sources = Source.objects.filter(qry, **constraints)
        if sources:
            return (True, sources[0].asset)
        else:
            return (True, None)

    def by_course_and_user(self, course, user):
        # returns the assets in a user's "collection"
        assets = Asset.objects.filter(
            course=course,
            sherdnote_set__author=user,
            sherdnote_set__is_global_annotation=True
        ).distinct()
        return assets.select_related('course', 'author')

    def by_course(self, course):
        assets = Asset.objects.filter(course=course) \
            .extra(select={'lower_title': 'lower(assetmgr_asset.title)'}) \
            .distinct()
        return assets.select_related('course', 'author')

    def migrate(self, assets, course, user, faculty, object_map,
                include_tags, include_notes):
        from mediathread.djangosherd.models import SherdNote
        for old_asset in assets:
            if old_asset.id not in object_map['assets']:
                new_asset = Asset.objects.migrate_one(old_asset,
                                                      course,
                                                      user)

                object_map['assets'][old_asset.id] = new_asset

                notes = SherdNote.objects.get_related_notes(
                    [old_asset], None, faculty, True)

                # remove all extraneous global annotations
                notes = notes.filter(author__id__in=faculty)

                for old_note in notes:
                    if (old_note.id not in object_map['notes']):
                        new_note = SherdNote.objects.migrate_one(
                            old_note, new_asset, user,
                            include_tags, include_notes)
                        object_map['notes'][old_note.id] = new_note

        return object_map

    def migrate_one(self, asset, course, user):
        # Check to see if an asset exists with this mo already
        new_asset = None

        for o in Asset.objects.filter(title=asset.title, course=course,
                                      author=user):
            if (o.primary.label == asset.primary.label and
                    o.primary.url == asset.primary.url):
                new_asset = o
                break

        if not new_asset:
            new_asset = Asset(title=asset.title,
                              course=course,
                              author=user,
                              metadata_blob=asset.metadata_blob)

            original_author = (asset.get_metadata(METADATA_ORIGINAL_OWNER) or
                               asset.author.get_full_name())
            new_asset.add_metadata(METADATA_ORIGINAL_OWNER, original_author)

            new_asset.save()

            for source in asset.source_set.all():
                new_source = Source(asset=new_asset,
                                    label=source.label,
                                    url=source.url,
                                    primary=source.primary,
                                    media_type=source.media_type,
                                    size=source.size,
                                    height=source.height,
                                    width=source.width)
                new_source.save()

            new_asset.global_annotation(user, auto_create=True)

        return new_asset


class Asset(models.Model):
    objects = AssetManager()  # custom manager

    added = models.DateTimeField('date created',
                                 editable=False,
                                 auto_now_add=True)

    modified = models.DateTimeField('date modified',
                                    editable=False,
                                    auto_now=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    course = models.ForeignKey(
        Course, related_name='asset_set', on_delete=models.CASCADE)

    active = models.BooleanField(default=True)

    title = models.CharField(max_length=1024)

    transcript = models.TextField(
        null=True, blank=True,
        help_text='Transcript for audio/video media')

    # make it json or somethin
    metadata_blob = models.TextField(
        blank=True,
        help_text="Be careful, this is a JSON blob and NOT a place to enter "
        "the description, etc, and is easy to format incorrectly. "
        "Make sure not to add any \"'s.")

    # Labels which determine the saving of an asset
    # in order of priority for which label is marked primary.
    # An asset must have at least one source label from this list.
    primary_labels = (
        'flv', 'flv_pseudo', 'flv_rtmp',
        'mp4', 'mp4_pseudo', 'mp4_rtmp',
        'youtube', 'ogg', 'vimeo',
        'video_pseudo', 'video_rtmp', 'video',
        'mp3', 'mp4_audio', 'mp4_panopto',
        'image_fpx', 'image_fpxid',  # artstor.org
        'image',
        'pdf',
    )

    class Meta:
        permissions = (("can_upload_for", "Can upload assets for others"),)

    @classmethod
    def good_args(cls, args):
        """Do these args have anything in common with primary_labels?

        Returns whether args has any arguments that can be used for a
        Mediathread Asset.
        """
        return set(cls.primary_labels) & set(args.keys())

    def __str__(self):
        return u'%s <%r> (%s)' % (self.title, self.pk, self.course.title)

    def metadata(self):
        if self.metadata_blob:
            try:
                return json.loads(str(self.metadata_blob))
            except ValueError:
                pass

        return {}

    def get_metadata(self, key):
        metadata = self.metadata()
        try:
            return metadata[key]
        except KeyError:
            return ''

    def add_metadata(self, key, value):
        metadata = self.metadata()
        metadata[key] = value
        self.metadata_blob = json.dumps(metadata)

    def upload_references(self):
        try:
            value = self.get_metadata('wardenclyffe-id')
            q = '"wardenclyffe-id": ["{}"]'.format(value[0])
            return Asset.objects.filter(metadata_blob__contains=q).count()
        except IndexError:
            return 0

    def get_absolute_url(self):
        return reverse('asset-view', args=(self.pk,))

    @property
    def html_source(self):
        return self.source_set.get(asset=self, label='url')

    def xmeml_source(self):
        return self.sources.get('xmeml', None)

    @property
    def sources(self):
        return dict([(s.label, s) for s in Source.objects.filter(asset=self)])

    def _primary_cache_key(self):
        return '%s:primary' % (self.id)

    @property
    def primary(self):
        key = self._primary_cache_key()
        the_primary = cache.get(key)
        if the_primary is None:
            the_primary = self.source_set.get(primary=True)
            cache.set(key, the_primary)
        return the_primary

    def update_primary(self, label, url):
        s = self.primary
        s.label = label
        s.url = url
        s.save()

        # reset cached values
        cache.set(self._primary_cache_key(), s)

    @property
    def thumb_url(self):
        key = "%s:thumb" % (self.id)
        if key not in cache:
            try:
                url = self.source_set.get(label='thumb').url
            except Source.DoesNotExist:
                url = None
            cache.set(key, url)
        return cache.get(key)

    def tags(self):
        # returns all tags for this instance's notes
        return Tag.objects.usage_for_queryset(self.sherdnote_set.all())

    def filter_tags_by_users(self, users, counts=False):
        tags = Tag.objects.usage_for_queryset(
            self.sherdnote_set.filter(author__in=users), counts=counts)
        return sorted(tags, key=lambda tag: tag.name.lower())

    def global_annotation(self, user, auto_create=True):
        from mediathread.djangosherd.models import SherdNote
        return SherdNote.objects.global_annotation(
            self, user,
            auto_create=auto_create)[0]

    def media_type(self):
        label = 'video'
        if self.primary.is_image():
            label = 'image'
        elif self.primary.is_audio():
            label = 'audio'
        elif self.primary.is_pdf():
            label = 'pdf'

        return label

    def save_tag(self, user, tag):
        """
        adds a single tags to asset by user. if the user has already
        annotated the asset with this tag, this function does nothing.

        returns True iff this is the first time the given user
        is tagging the asset .. though it'd be nicer to return
        whether this function actually did anything.
        """
        from mediathread.djangosherd.models import SherdNote
        bucket, created = SherdNote.objects.global_annotation(self, user)
        bucket.add_tag(tag)
        bucket.save()
        return created

    request = None

    def update_references_in_string(self, text, old_asset):
        # substitute my id for an old asset id
        regex_string = \
            (r'(name=|href=|openCitation\()([\'"]/asset/)(%s)(/[^a])'
             % (old_asset.id))
        sub = r'\g<1>\g<2>%s\g<4>' % (self.id)
        return re.sub(regex_string, sub, text)

    def user_analysis_count(self, user):
        # global notes y/n + global tag count + annotation count
        count = 0
        gann = self.global_annotation(user, False)
        annotations = self.sherdnote_set.filter(author=user)
        if gann:
            if gann.body and len(gann.body) > 0:
                count += 1
            if gann.tags and len(gann.tags) > 0:
                count += len(gann.tags_split())

            annotations = annotations.exclude(id=gann.id)

        count += annotations.count()
        return count


class S3PrivateFileField(models.FileField):
    """
    A FileField that gives the 'private' ACL to the files it uploads
    to S3, instead of the default ACL.
    """
    def __init__(
            self, verbose_name=None, name=None,
            upload_to='', storage=None, **kwargs
    ):
        super(S3PrivateFileField, self).__init__(
            verbose_name=verbose_name, name=name,
            upload_to=upload_to, storage=private_storage,
            **kwargs
        )


class Source(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)

    # hint on source's nature, e.g. thumbnail
    # should be generally human readable
    label = models.CharField(max_length=64)

    url = models.TextField()

    upload = S3PrivateFileField(upload_to='uploads/', blank=True)

    # only one Source per asset should have primary=True
    # This should help indicate what 'kind' of thing
    # the asset is, so one with label 'quicktime' as primary
    # is a movie, even though it might have image urls for thumbs, etc
    primary = models.BooleanField(default=False, db_index=True)

    media_type = models.CharField(
        default=None, null=True, blank=True, max_length=64)

    # in bytes (like FileField)
    size = models.PositiveIntegerField(default=0)

    # obvious for visual media
    # you can hack this to use it for things like
    # multi-dimensional sizes: e.g. wordcount
    height = models.PositiveSmallIntegerField(default=0)
    width = models.PositiveSmallIntegerField(default=0)

    modified = models.DateTimeField('date modified',
                                    editable=False,
                                    auto_now=True)

    def __str__(self):
        return '[%s] %s' % (self.label, smart_text(self.asset))

    def is_image(self):
        return (self.label == 'poster' or
                self.label == "image" or
                self.label == "image_fpxid" or
                self.label == "image_fpx" or
                (self.media_type and self.media_type.startswith('image/')))

    def is_audio(self):
        return self.label == 'mp3' or self.label == 'mp4_audio'

    def is_pdf(self):
        return self.label == 'pdf'

    def is_panopto(self):
        return self.label == 'mp4_panopto'

    def signed_url(self):
        s3_private_bucket = getattr(
            settings,
            'S3_PRIVATE_STORAGE_BUCKET_NAME',
            'mediathread-private-uploads')
        if s3_private_bucket in self.url:
            return get_signed_s3_url(
                self.url, s3_private_bucket,
                settings.AWS_ACCESS_KEY,
                settings.AWS_SECRET_KEY)

        if self.upload:
            return self.upload.url

        return self.url

    def url_processed(self, request):
        s3_private_bucket = getattr(
            settings,
            'S3_PRIVATE_STORAGE_BUCKET_NAME',
            'mediathread-private-uploads')
        if s3_private_bucket in self.url:
            return get_signed_s3_url(
                self.url, s3_private_bucket,
                settings.AWS_ACCESS_KEY,
                settings.AWS_SECRET_KEY)

        url_processor = getattr(settings, 'ASSET_URL_PROCESSOR')
        return url_processor(self.url, self.label, request)


class ExternalCollection(models.Model):
    title = models.CharField(max_length=1024)
    url = models.CharField(max_length=1024)
    thumb_url = models.CharField(max_length=1024, null=True, blank=True)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    uploader = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        unique_together = ("title", "course")


class SuggestedExternalCollection(models.Model):
    title = models.CharField(max_length=1024, unique=True)
    url = models.CharField(max_length=1024)
    thumb_url = models.CharField(max_length=1024)
    description = models.TextField()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
