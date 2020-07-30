# pylint: disable-msg=R0904
import json
import time
from django.urls import reverse
from mediathread.api import ClassLevelAuthentication, UserResource
from mediathread.assetmgr.models import Asset, Source
from mediathread.djangosherd.api import SherdNoteResource
from tastypie import fields
from tastypie.resources import ModelResource


def add_note_ctx_to_json(note_ctx, the_json):
    if note_ctx['is_global_annotation']:
        the_json['global_annotation'] = note_ctx

        the_json['global_annotation_analysis'] = (
            len(note_ctx['vocabulary']) > 0 or
            len(note_ctx['metadata']['body']) > 0 or
            len(note_ctx['metadata']['tags']) > 0)
    else:
        the_json['annotations'].append(note_ctx)
    return the_json


class AssetResource(ModelResource):

    author = fields.ForeignKey(UserResource, 'author', full=True)

    class Meta:
        queryset = Asset.objects.none()
        excludes = ['added', 'course',
                    'active', 'metadata_blob']
        list_allowed_methods = []
        detail_allowed_methods = []
        authentication = ClassLevelAuthentication()
        ordering = ['added', 'modified', 'id', 'title', 'author']

    def __init__(self, *args, **kwargs):
        # @todo: extras is a side-effect of the Mustache templating system
        # not supporting the ability to reference variables in the parent
        # context. ideally, the templating system should be switched out to
        # something more reasonable
        self.extras = kwargs.pop('extras', {})

        self.include_annotations = kwargs.pop('include_annotations', True)
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

        if hasattr(self, 'request') and hasattr(self.request, 'course'):
            bundle.data['local_url'] = reverse(
                'asset-view', kwargs={
                    'course_pk': self.request.course.pk,
                    'asset_id': bundle.obj.pk,
                })
        else:
            bundle.data['local_url'] = bundle.obj.get_absolute_url()

        bundle.data['media_type_label'] = bundle.obj.media_type()
        bundle.data['editable_title'] = (
            bundle.request.user.is_staff or
            bundle.obj.author == bundle.request.user)

        bundle.data['annotations'] = []
        bundle.data['annotation_count'] = 0
        bundle.data['my_annotation_count'] = 0
        bundle.data['added'] = self.format_time(bundle.obj.added)
        bundle.data['modified'] = self.format_time(bundle.obj.modified)

        sources = {}
        for s in bundle.obj.source_set.all():
            sources[s.label] = {'label': s.label,
                                'url': s.url_processed(bundle.request),
                                'width': s.width,
                                'height': s.height,
                                'primary': s.primary}
        bundle.data['sources'] = sources

        for key, value in self.extras.items():
            bundle.data[key] = value

        return bundle

    def render_one(self, request, asset, notes=None):
        self.request = request
        try:
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

            if notes:
                note_resource = SherdNoteResource()
                for note in notes:
                    note_ctx = note_resource.render_one(request, note, "")
                    the_json = add_note_ctx_to_json(note_ctx, the_json)
            return the_json

        except Source.DoesNotExist:
            return None

    def render_one_context(self, request, asset, notes=None):
        ctx = {
            'assets': {
                asset.pk: self.render_one(request, asset, notes)
            }
        }
        return ctx

    def update_asset_context(self, request, ctx, asset):
        if asset.id not in ctx:
            abundle = self.build_bundle(obj=asset, request=request)
            dehydrated = self.full_dehydrate(abundle)
            asset_ctx = self._meta.serializer.to_simple(dehydrated, None)
            asset_ctx['tags'] = [tag.name for tag in asset.tags()]
            ctx[asset.id] = asset_ctx

    def update_note_context(self, request, ctx, note_res, note, owner, viewer):
        is_global = note.is_global_annotation()
        if not is_global:
            ctx[note.asset.id]['annotation_count'] += 1
            if note.author == viewer:
                ctx[note.asset.id]['my_annotation_count'] += 1

        if note.modified > note.asset.modified:
            ctx[note.asset.id]['modified'] = self.format_time(note.modified)

        if self.include_annotations:
            note_ctx = note_res.render_one(request, note, "")

            if is_global:
                if note.author == owner:
                    ctx[note.asset.id]['global_annotation'] = note_ctx
            else:
                ctx[note.asset.id]['annotations'].append(note_ctx)

    def render_list(self, request, record_owner, record_viewer, assets, notes):
        self.request = request
        note_resource = SherdNoteResource()
        ctx = {}

        for asset in assets.all():
            self.update_asset_context(request, ctx, asset)

        for note in notes.all():
            try:
                note.asset.primary

                self.update_note_context(
                    request, ctx, note_resource, note,
                    record_owner, record_viewer)

            except Source.DoesNotExist:
                pass  # don't break in this situation

        values = ctx.values()
        return list(values)

    def alter_list_data_to_serialize(self, request, to_be_serialized):
        to_be_serialized['objects'] = sorted(
            to_be_serialized['objects'],
            key=lambda bundle: bundle.data['modified'],
            reverse=True)
        return to_be_serialized
