from courseaffils.models import Course
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.query_utils import Q
from tagging.models import Tag
import json
import re


def default_url_processor(source, request, obj=None):
    return source.url

# Override in deploy_specific/settings.py
# for special authentication processing
# Called by Source:url_processed
url_processor = getattr(settings, 'ASSET_URL_PROCESSOR', default_url_processor)


class AssetManager(models.Manager):
    def get_by_args(self, args, **constraints):
        "args typically is request.GET"
        criteria = Asset.good_args(args)
        if not criteria:
            return False

        qry = reduce(lambda x, y: x | y,  # composable Q's
                     [models.Q(label=k, url=args[k], primary=True)
                      for k in criteria])
        sources = Source.objects.filter(qry, **constraints)
        if sources:
            return sources[0].asset
        else:
            return None

    def archives(self):
        return self.filter(Q(source__primary=True) &
                           Q(source__label='archive'))

    def by_course_and_user(self, course, user):
        # returns the assets in a user's "collection"
        assets = Asset.objects.filter(course=course,
                                      sherdnote_set__author=user,
                                      sherdnote_set__range1=None).distinct()

        # Exclude archives from these lists
        assets = assets.exclude(Q(source__primary=True) &
                                Q(source__label='archive'))
        return assets.order_by('-sherdnote_set__modified').select_related()

    def by_course(self, course):
        assets = Asset.objects.filter(course=course) \
            .extra(select={'lower_title': 'lower(assetmgr_asset.title)'}) \
            .distinct().select_related().order_by('lower_title')

        # Exclude archives from these lists
        assets = assets.exclude(Q(source__primary=True) &
                                Q(source__label='archive'))
        return assets.order_by('-sherdnote_set__modified')

    def migrate(self, assets, course, user, faculty, object_map):
        note_model = models.get_model('djangosherd', 'sherdnote')
        for old_asset in assets:
            if old_asset.id not in object_map['assets']:
                new_asset = Asset.objects.migrate_one(old_asset,
                                                      course,
                                                      user)
                object_map['assets'][old_asset.id] = new_asset

                notes = note_model.objects.get_related_notes(
                    [old_asset], None, faculty)

                for old_note in notes:
                    if (not old_note.is_global_annotation() and
                            old_note.id not in object_map['notes']):
                        new_note = note_model.objects.migrate_one(old_note,
                                                                  new_asset,
                                                                  user)
                        object_map['notes'][old_note.id] = new_note

                # migrate the requesting user's global annotation
                # on this asset, if it exists
                gann = old_asset.global_annotation(user, False)
                if gann:
                    note_model.objects.migrate_one(gann, new_asset, user)

        return object_map

    def migrate_one(self, asset, course, user):
        # Check to see if an asset exists with this mo already
        new_asset = None
        try:
            new_asset = Asset.objects.get(title=asset.title,
                                          course=course,
                                          author=user,
                                          metadata_blob=asset.metadata_blob)
            if (new_asset.primary.label != asset.primary.label or
                    new_asset.primary.url != asset.primary.url):
                new_asset = None
        except Asset.DoesNotExist:
            pass

        if not new_asset:
            new_asset = Asset(title=asset.title,
                              course=course,
                              author=user,
                              metadata_blob=asset.metadata_blob)
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

    author = models.ForeignKey(User)

    course = models.ForeignKey(Course, related_name='asset_set')

    active = models.BooleanField(default=True)

    title = models.CharField(max_length=1024)

    # make it json or somethin
    metadata_blob = models.TextField(
        blank=True,
        help_text="""Be careful, this is a JSON blob and NOT a place to enter \
        the description, etc, and is easy to format incorrectly. \
        Make sure not to add any "'s.""")

    # labels which determine the saving of an asset
    # in order of priority for which label is marked primary
    # an asset must have at least one source label from this list
    # 'url' should probably stay at the end
    useful_labels = ('flv', 'flv_pseudo', 'flv_rtmp',
                     'mp4', 'mp4_pseudo', 'mp4_rtmp',
                     'youtube', 'quicktime', 'realplayer',
                     'ogg', 'vimeo', 'kaltura',
                     'video_pseudo', 'video_rtmp', 'video',
                     'mp3', 'mp4_audio',
                     'image_fpx', 'image_fpxid',  # artstor.org
                     'image')

    # not good for uniqueness
    fundamental_labels = ('archive', 'url',)
    primary_labels = useful_labels + fundamental_labels

    class Meta:
        permissions = (("can_upload_for", "Can upload assets for others"),)

    @classmethod
    def good_args(cls, args):
        return set(cls.primary_labels) & set(args.keys())

    def __unicode__(self):
        return u'%s <%r> (%s)' % (self.title, self.pk, self.course.title)

    def metadata(self):
        if self.metadata_blob:
            try:
                return json.loads(str(self.metadata_blob))
            except:  # presumably json decoding, but let's quiet everything
                return {}
        return {}

    @models.permalink
    def get_absolute_url(self):
        return ('asset-view', (), {'asset_id': self.pk, })

    @property
    def html_source(self):
        return Source.objects.get(asset=self, label='url')

    def xmeml_source(self):
        return self.sources.get('xmeml', None)

    @property
    def sources(self):
        return dict([(s.label, s) for s in Source.objects.filter(asset=self)])

    @property
    def primary(self):
        primary_cache = getattr(self, '_primary_cache', None)
        if primary_cache:
            return primary_cache
        self._primary_cache = Source.objects.get(asset=self, primary=True)
        return self._primary_cache

    @property
    def thumb_url(self):
        if not hasattr(self, '_thumb_url'):
            try:
                self._thumb_url = \
                    Source.objects.get(asset=self, label='thumb').url
            except Source.DoesNotExist:
                self._thumb_url = None
        return self._thumb_url

    def tags(self):
        # returns all tags for this instance's notes
        return Tag.objects.usage_for_queryset(self.sherdnote_set.all())

    def filter_tags_by_users(self, users, counts=False):
        tags = Tag.objects.usage_for_queryset(
            self.sherdnote_set.filter(author__in=users), counts=counts)
        tags.sort(lambda a, b: cmp(a.name.lower(), b.name.lower()))
        return tags

    def global_annotation(self, user, auto_create=True):
        note_model = models.get_model('djangosherd', 'sherdnote')
        return note_model.objects.global_annotation(self, user,
                                                    auto_create=auto_create)[0]

    def media_type(self):
        label = 'video'
        if self.primary.is_image():
            label = 'image'
        elif self.primary.is_audio():
            label = 'audio'

        return label

    def save_tag(self, user, tag):
        """
        adds a single tags to asset by user. if the user has already
        annotated the asset with this tag, this function does nothing.

        returns True iff this is the first time the given user
        is tagging the asset .. though it'd be nicer to return
        whether this function actually did anything.
        """
        note_model = models.get_model('djangosherd', 'sherdnote')
        if note_model:
            bucket, created = note_model.objects.global_annotation(self, user)
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

        count += len(annotations)
        return count


class Source(models.Model):
    asset = models.ForeignKey(Asset)

    # hint on source's nature, e.g. thumbnail
    # should be generally human readable
    label = models.CharField(max_length=64)

    # should this support URI fragments?
    # file:/// for local files?
    url = models.CharField(max_length=4096)

    # only one Source per asset should have primary=True
    # This should help indicate what 'kind' of thing
    # the asset is, so one with label 'quicktime' as primary
    # is a movie, even though it might have image urls for thumbs, etc
    primary = models.BooleanField(default=False)

    media_type = models.CharField(default=None, null=True, max_length=64)

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

    def __unicode__(self):
        asset = u'No Asset'
        if self.asset_id:  # defensive for non-saved sources w/o an asset
            asset = self.asset
        return u'[%s] %s' % (self.label, unicode(asset))

    def is_image(self):
        return (self.label == 'poster' or
                self.label == "image" or
                self.label == "image_fpx" or
                (self.media_type and self.media_type.startswith('image/')))

    def is_audio(self):
        return self.label == 'mp3' or self.label == 'mp4_audio'

    def is_archive(self):
        return self.label == 'archive'

    def url_processed(self, request, obj=None):
        return url_processor(self, request, obj)


class SupportedSource(models.Model):
    title = models.CharField(max_length=1024)
    archive_url = models.CharField(max_length=1024)
    thumb_url = models.CharField(max_length=1024)
    description = models.TextField()

    def __unicode__(self):
        return self.title
