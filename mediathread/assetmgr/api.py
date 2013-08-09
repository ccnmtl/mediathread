from mediathread.api import ClassLevelAuthentication, UserResource, \
    ToManyFieldEx
from mediathread.assetmgr.models import Asset
from mediathread.djangosherd.api import SherdNoteResource
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.resources import ModelResource
import simplejson


class AssetAuthorization(Authorization):

    def apply_limits(self, request, object_list):

        invisible = []
        for asset in object_list:
            if not asset.course.is_member(request.user):
                invisible.append(asset.id)

        object_list = object_list.exclude(id__in=invisible)
        return object_list.order_by('id')


class AssetResource(ModelResource):
    def __init__(self,
                 include_annotations=True,
                 owner_selections_are_visible=False,
                 record_owner=None,
                 extras={}):
        super(ModelResource, self).__init__(None)

        self.options = {
            'include_annotations': include_annotations,
            'owner_selections_are_visible': owner_selections_are_visible,
            'record_owner': record_owner
        }
        self.extras = extras

    author = fields.ForeignKey(UserResource, 'author', full=True)

    sherdnote_set = ToManyFieldEx(
        'mediathread.djangosherd.api.SherdNoteResource',
        'sherdnote_set',
        blank=True, null=True, full=True)

    class Meta:
        queryset = Asset.objects.all().order_by('id')
        excludes = ['added', 'modified', 'course', 'active', 'metadata_blob']
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        authentication = ClassLevelAuthentication()
        authorization = AssetAuthorization()

        ordering = ['id', 'title']

        filtering = {
            'author': ALL_WITH_RELATIONS,
            'sherdnote_set': ALL_WITH_RELATIONS
        }

    def apply_filters(self, request, applicable_filters):
        qs = self.get_object_list(request).filter(**applicable_filters)
        return qs.distinct()

    def dehydrate(self, bundle):
        bundle.data['thumb_url'] = bundle.obj.thumb_url
        bundle.data['primary_type'] = bundle.obj.primary.label
        bundle.data['local_url'] = bundle.obj.get_absolute_url()
        bundle.data['media_type_label'] = bundle.obj.media_type()

        try:
            metadata = simplejson.loads(bundle.obj.metadata_blob)
            metadata = [{'key': k, 'value': v} for k, v in metadata.items()]
            bundle.data['metadata'] = metadata
        except ValueError:
            pass

        sources = {}
        for s in bundle.obj.source_set.all():
            sources[s.label] = {'label': s.label,
                                'url': s.url_processed(bundle.request),
                                'width': s.width,
                                'height': s.height,
                                'primary': s.primary}
        bundle.data['sources'] = sources

        bundle.data['annotations'] = []
        bundle.data['annotation_count'] = len(bundle.data['sherdnote_set'])
        bundle.data['my_annotation_count'] = 0

        # the sherdnote_set authorization has been applied
        # I'm filtering here rather than directly on the sherdnote resource
        # As counts need to be displayed for all, then the subset
        for note in bundle.data['sherdnote_set']:
            if note.obj.author == bundle.request.user:
                bundle.data['my_annotation_count'] += 1

            if self.options['include_annotations']:
                if self.options['record_owner']:
                    if note.obj.author == self.options['record_owner']:
                        bundle.data['annotations'].append(note.data)
                else:
                    bundle.data['annotations'].append(note.data)

        # include the global_annotation for the user as well
        if self.options['include_annotations']:
            if (self.options['record_owner'] and
                    self.options['owner_selections_are_visible']):
                ga = bundle.obj.global_annotation(
                    self.options['record_owner'], auto_create=False)
            else:
                ga = bundle.obj.global_annotation(bundle.request.user,
                                                  auto_create=False)

            if ga:
                bundle.data['global_annotation'] = \
                    SherdNoteResource().render_one(bundle.request, ga, '')
                bundle.data['global_annotation_analysis'] = (
                    (ga.tags is not None and len(ga.tags) > 0) or
                    (ga.body is not None and len(ga.body) > 0))
            else:
                bundle.data['global_annotation_analysis'] = False

        for key, value in self.extras.items():
            bundle.data[key] = self.extras[key]

        bundle.data.pop('sherdnote_set')
        return bundle

    def render_one(self, request, item):
        bundle = self.build_bundle(obj=item, request=request)
        dehydrated = self.full_dehydrate(bundle)
        return self._meta.serializer.to_simple(dehydrated, None)

    def render_list(self, request, lst):
        asset_json = []
        for asset in lst:
            the_json = self.render_one(request, asset)
            asset_json.append(the_json)
        return asset_json
