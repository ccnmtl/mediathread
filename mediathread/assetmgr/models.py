from courseaffils.models import Course
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from tagging.models import Tag
import re
import simplejson


def default_url_processor(source, request):
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

        q = reduce(lambda x, y: x | y,  # composable Q's
                   [models.Q(label=k, url=args[k], primary=True)
                    for k in criteria])
        sources = Source.objects.filter(q, **constraints)
        if sources:
            return sources[0].asset
        else:
            return None

    def archives(self):
        return self.filter(source__primary=True, source__label='archive')

    def annotated_by(self, course, user, include_archives=False):
        assets = Asset.objects.filter(course=course)
        fassets = assets.filter(
            sherdnote_set__author=user, sherdnote_set__range1=None).distinct()\
            .order_by('-sherdnote_set__modified').select_related()
        if include_archives:
            return fassets
        else:
            to_return = []
            for asset in fassets:
                if asset.primary.label != 'archive':
                    to_return.append(asset)
            return to_return

    def migrate(self, asset_set, course, user, object_map):
        SherdNote = models.get_model('djangosherd', 'sherdnote')
        for asset_json in asset_set:
            if asset_json['id'] not in object_map['assets']:
                old_asset = Asset.objects.get(id=asset_json['id'])
                new_asset = Asset.objects.migrate_one(old_asset,
                                                      course,
                                                      user)
                object_map['assets'][old_asset.id] = new_asset

                annotations = []

                if "annotations" in asset_json:
                    annotations = annotations + asset_json["annotations"]

                for note_json in annotations:
                    if note_json["id"] not in object_map['notes']:
                        old_note = SherdNote.objects.get(
                            id=note_json["id"])
                        new_note = SherdNote.objects.migrate_one(old_note,
                                                                 new_asset,
                                                                 user)
                        # Don't count global annotations
                        object_map['notes'][old_note.id] = new_note

                # migrate the requesting user's global annotation
                # on this asset, if it exists
                ga = old_asset.global_annotation(user, False)
                if ga:
                    SherdNote.objects.migrate_one(ga, new_asset, user)

        return object_map

    def migrate_one(self, asset, course, user):
        # Check to see if an asset exists with this mo already
        x = None
        try:
            x = Asset.objects.get(title=asset.title,
                                  course=course,
                                  author=user,
                                  metadata_blob=asset.metadata_blob)
            if (x.primary.label != asset.primary.label or
                    x.primary.url != asset.primary.url):
                x = None
        except Asset.DoesNotExist:
            pass

        if not x:
            x = Asset(title=asset.title,
                      course=course,
                      author=user,
                      metadata_blob=asset.metadata_blob)
            x.save()

            for source in asset.source_set.all():
                s = Source(asset=x,
                           label=source.label,
                           url=source.url,
                           primary=source.primary,
                           media_type=source.media_type,
                           size=source.size,
                           height=source.height,
                           width=source.width)
                s.save()

            x.global_annotation(user, auto_create=True)

        return x


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
                     'image_fpx',  # artstor.org and FSI flash image viewer
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
                return simplejson.loads(str(self.metadata_blob))
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
        p = getattr(self, '_primary_cache', None)
        if p:
            return p
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
        SherdNote = models.get_model('djangosherd', 'sherdnote')
        if SherdNote:
            return SherdNote.objects.global_annotation(
                self, user, auto_create=auto_create)[0]

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
        SherdNote = models.get_model('djangosherd', 'sherdnote')
        if SherdNote:
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
        ga = self.global_annotation(user, False)
        annotations = self.sherdnote_set.filter(author=user)
        if ga:
            if ga.body and len(ga.body) > 0:
                count += 1
            if ga.tags and len(ga.tags) > 0:
                count += len(ga.tags_split())

            annotations = annotations.exclude(id=ga.id)

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

    def url_processed(self, request):
        return url_processor(self, request)


class SupportedSource(models.Model):
    title = models.CharField(max_length=1024)
    archive_url = models.CharField(max_length=1024)
    thumb_url = models.CharField(max_length=1024)
    description = models.TextField()

    def __unicode__(self):
        return self.title
