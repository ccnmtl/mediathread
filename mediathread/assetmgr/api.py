from datetime import date
from django.contrib.contenttypes.models import ContentType
from django.db.models.query_utils import Q
from mediathread.api import ClassLevelAuthentication, UserResource, \
    ToManyFieldEx
from mediathread.assetmgr.models import Asset, Source
from mediathread.djangosherd.api import SherdNoteResource
from mediathread.djangosherd.models import SherdNote
from mediathread.taxonomy.models import TermRelationship
from tagging.models import TaggedItem
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.resources import ModelResource
import simplejson


class SourceResource(ModelResource):
    class Meta:
        queryset = Source.objects.none()
        resource_name = 'source'
        allowed_methods = ['get']

    def dehydrate(self, bundle):
        bundle.data['url'] = bundle.obj.url_processed(bundle.request),
        return bundle


class AssetAuthorization(Authorization):

    def has_vocabulary(self, notes, vocabulary):
        # OR'd within vocabulary, AND'd across vocabulary
        has_relationships = True
        content_type = ContentType.objects.get_for_model(SherdNote)
        for vocabulary_id in vocabulary:
            relationships = TermRelationship.objects.filter(
                content_type_id=content_type,
                object_id__in=[n.id for n in notes],
                term__id__in=vocabulary[vocabulary_id],
                term__vocabulary__id=vocabulary_id)
            has_relationships = len(relationships) > 0 and has_relationships
        return has_relationships

    def is_tagged(self, notes, tag_string):
        items = TaggedItem.objects.get_union_by_model(notes, tag_string)
        return len(items) > 0

    def in_date_range(self, notes, date_range):
        enddate = date.today()
        if date_range == 'today':
            startdate = enddate + date.timedelta(-1)
        elif date_range == 'yesterday':
            startdate = enddate + date.timedelta(-2)
        elif date_range == 'lastweek':
            startdate = enddate + date.timedelta(-7)

        items = notes.filter(Q(added__range=[startdate, enddate]) |
                             Q(modified__range=[startdate, enddate]))

        return len(items) > 0

    def apply_limits(self, request, object_list):
        invisible = []
        archives = list(request.course.asset_set.archives())

        tag_string = request.GET.get('tag', '')
        modified = request.GET.get('modified', '')
        vocabulary = dict((key[len('vocabulary-'):], val.split(","))
                          for key, val in request.GET.items()
                          if key.startswith('vocabulary-'))

        for asset in object_list:
            notes = SherdNoteResource().apply_authorization_limits(
                request, asset.sherdnote_set)

            if not asset.course.is_member(request.user):
                invisible.append(asset.id)
            elif asset in archives:
                invisible.append(asset.id)
            elif len(tag_string) > 0 and not self.is_tagged(notes, tag_string):
                invisible.append(asset.id)
            elif len(modified) > 0 and not self.in_date_range(notes, modified):
                invisible.append(asset.id)
            elif (len(vocabulary) > 0 and
                  not self.has_vocabulary(notes, vocabulary)):
                invisible.append(asset.id)

        return object_list.exclude(id__in=invisible).order_by('id')


class AssetResource(ModelResource):
    def __init__(self,
                 include_annotations=True,
                 include_archives=False,
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

#     source = fields.ToManyFieldEx(
#         'mediathread.assetmgr.api.SourceResource',
#         'source_set',
#         blank=True, null=True, full=True)

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
        bundle.data['annotation_count'] = 0
        bundle.data['my_annotation_count'] = 0

        # the sherdnote_set authorization has been applied
        # I'm filtering here rather than directly on the sherdnote resource
        # As counts need to be displayed for all, then the user subset
        # and global annotation display logic is a bit intricate
        for note in bundle.data['sherdnote_set']:
            if not note.data['is_global_annotation']:
                bundle.data['annotation_count'] += 1
                if note.obj.author == bundle.request.user:
                    bundle.data['my_annotation_count'] += 1

            if (self.options['include_annotations'] and
                    not note.data['is_global_annotation']):
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

    def render_list(self, request, object_list):
        object_list = self.apply_authorization_limits(request, object_list)
        asset_json = []
        for asset in object_list:
            the_json = self.render_one(request, asset)
            asset_json.append(the_json)
        return asset_json
