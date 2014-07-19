#pylint: disable-msg=R0904
from django.db.models.aggregates import Max
from mediathread.api import ClassLevelAuthentication, UserResource
from mediathread.assetmgr.models import Asset, Source
from mediathread.djangosherd.api import SherdNoteResource
from mediathread.djangosherd.models import SherdNote
from mediathread.main.models import UserSetting
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.bundle import Bundle
from tastypie.resources import ModelResource
import json
import time


class SourceResource(ModelResource):
    class Meta:
        queryset = Source.objects.none()
        resource_name = 'source'
        allowed_methods = ['get']
        excludes = ['id', 'modified', 'size', 'media_type']

    def dehydrate(self, bundle):
        bundle.data['url'] = bundle.obj.url_processed(bundle.request,
                                                      bundle.obj.asset),
        return bundle


class AssetAuthorization(Authorization):

    def get_related_notes(self, assets, bundle):
        request = bundle.request
        tag_string = request.GET.get('tag', '')
        modified = request.GET.get('modified', '')
        vocabulary = dict((key[len('vocabulary-'):], val.split(","))
                          for key, val in request.GET.items()
                          if key.startswith('vocabulary-'))

        self.related_notes = SherdNote.objects.get_related_notes(
            assets, bundle.record_owner or None, bundle.visible_authors,
            tag_string, modified, vocabulary)

        # return the related asset ids
        return self.related_notes.values_list('asset__id', flat=True)

    def read_detail(self, object_list, bundle):
        ids = self.get_related_notes(object_list, bundle)
        return ids.count() > 0

    def read_list(self, object_list, bundle):
        object_list = object_list.filter(course=bundle.request.course)

        # return the related assets
        ids = self.get_related_notes(object_list, bundle)
        return object_list.filter(id__in=ids).distinct()


class AssetResource(ModelResource):

    author = fields.ForeignKey(UserResource, 'author', full=True)
    sources = fields.ToManyField(SourceResource, 'source_set',
                                 blank=True, null=True, full=True, )

    class Meta:
        queryset = Asset.objects.none()
        excludes = ['added', 'modified', 'course', 'active', 'metadata_blob']
        list_allowed_methods = []
        detail_allowed_methods = []
        authentication = ClassLevelAuthentication()
        authorization = AssetAuthorization()
        ordering = ['modified', 'id', 'title']

    def __init__(self, *args, **kwargs):
        self.record_owner = kwargs.pop('record_owner', None)
        self.visible_authors = kwargs.pop('visible_authors', [])
        self.include_annotations = kwargs.pop('include_annotations', True)
        self.extras = kwargs.pop('extras', {})

        self.offset = kwargs.pop('offset', 0)
        self.limit = kwargs.pop('limit', 0)

        super(AssetResource, self).__init__(*args, **kwargs)

    def format_time(self, dt):
        return dt.strftime("%m/%d/%y %I:%M %p")

    def to_time(self, dtstr):
        return time.strptime(dtstr, "%m/%d/%y %I:%M %p")

    def apply_filters(self, request, applicable_filters):
        qs = self.get_object_list(request).filter(**applicable_filters)
        return qs.distinct()

    def dehydrate(self, bundle):
        bundle.data['thumb_url'] = bundle.obj.thumb_url
        bundle.data['primary_type'] = bundle.obj.primary.label
        bundle.data['local_url'] = bundle.obj.get_absolute_url()
        bundle.data['media_type_label'] = bundle.obj.media_type()
        bundle.data['editable_title'] = (
            bundle.request.user.is_staff or
            bundle.obj.author == bundle.request.user)

        bundle.data['annotations'] = []
        bundle.data['annotation_count'] = 0
        bundle.data['my_annotation_count'] = 0
        bundle.data['modified'] = self.format_time(bundle.obj.modified)

        for key, value in self.extras.items():
            bundle.data[key] = value

        return bundle

    def render_one(self, request, asset):
        try:
            bundle = Bundle(request=request)
            bundle.record_owner = self.record_owner
            bundle.visible_authors = self.visible_authors

            # authorize the object, compiling visible notes
            if not self.authorized_read_detail([asset], bundle):
                return {}

            self.related_notes = self._meta.authorization.related_notes

            bundle = self.build_bundle(obj=asset, request=request)
            dehydrated = self.full_dehydrate(bundle)
            the_json = self._meta.serializer.to_simple(dehydrated, None)

            try:
                metadata = json.loads(bundle.obj.metadata_blob)
                metadata = [{'key': k, 'value': v}
                            for k, v in metadata.items()]
                the_json['metadata'] = metadata
            except ValueError:
                pass

            note_resource = SherdNoteResource()
            for note in self.related_notes:
                note_ctx = note_resource.render_one(request, note, "")

                if note.is_global_annotation():
                    the_json['global_annotation'] = note_ctx
                else:
                    the_json['annotations'].append(note_ctx)

            help_setting = UserSetting.get_setting(
                request.user, "help_item_detail_view", True)

            return {'type': 'asset',
                    'assets': {asset.pk: the_json},
                    'user_settings': {'help_item_detail_view': help_setting}}

        except Source.DoesNotExist:
            return None

    def render_list(self, request, object_list):
        bundle = Bundle(request=request)
        bundle.record_owner = self.record_owner
        bundle.visible_authors = self.visible_authors

        # filter the objects, compiling visible assets AND notes
        object_list = self.authorized_read_list(object_list, bundle)
        self.related_notes = self._meta.authorization.related_notes

        # sort the object list via aggregation on the visible notes
        assets = self.related_notes.values('asset')
        assets = assets.annotate(last_modified=Max('modified'))
        assets = assets.order_by('-last_modified')

        # paginate the list
        if self.limit:
            assets = assets[self.offset:self.offset + self.limit]
            ids = [a['asset'] for a in assets]
            active_notes = self.related_notes.filter(asset__id__in=ids)
        else:
            active_notes = self.related_notes

        # render assets + notes based on the active note list
        note_resource = SherdNoteResource()
        ctx = {}
        for note in active_notes.all():
            if note.asset.id not in ctx:
                abundle = self.build_bundle(obj=note.asset, request=request)
                dehydrated = self.full_dehydrate(abundle)
                asset_ctx = self._meta.serializer.to_simple(dehydrated, None)
                ctx[note.asset.id] = asset_ctx

            is_global = note.is_global_annotation()
            if not is_global:
                ctx[note.asset.id]['annotation_count'] += 1
                if note.author == self.record_owner:
                    ctx[note.asset.id]['my_annotation_count'] += 1

            if note.modified > note.asset.modified:
                ctx[note.asset.id]['modified'] = \
                    self.format_time(note.modified)

            if self.include_annotations:
                note_ctx = note_resource.render_one(request, note, "")

                if is_global:
                    ctx[note.asset.id]['global_annotation'] = note_ctx
                else:
                    ctx[note.asset.id]['annotations'].append(note_ctx)

        values = ctx.values()
        return sorted(values,
                      key=lambda value: self.to_time(value['modified']),
                      reverse=True)

    def alter_list_data_to_serialize(self, request, to_be_serialized):
        to_be_serialized['objects'] = sorted(
            to_be_serialized['objects'],
            key=lambda bundle: bundle.data['modified'],
            reverse=True)
        return to_be_serialized
