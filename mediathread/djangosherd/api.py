# pylint: disable-msg=R0904
from tastypie import fields
from tastypie.resources import ModelResource

from mediathread.api import UserResource, TagResource
from mediathread.assetmgr.models import Asset
from mediathread.djangosherd.models import SherdNote, DiscussionIndex
from mediathread.projects.models import ProjectNote
from mediathread.taxonomy.api import TermResource
from mediathread.taxonomy.models import TermRelationship


class SherdNoteResource(ModelResource):
    author = fields.ForeignKey(UserResource, 'author',
                               full=True, null=True, blank=True)

    class Meta:
        queryset = SherdNote.objects.select_related('asset').order_by("id")
        excludes = ['tags', 'body', 'added', 'modified']
        list_allowed_methods = []
        detail_allowed_methods = []

    def dehydrate(self, bundle):
        try:
            bundle.data['is_global_annotation'] = \
                bundle.obj.is_global_annotation()
            bundle.data['asset_id'] = str(bundle.obj.asset.id)
            bundle.data['is_null'] = bundle.obj.is_null()
            bundle.data['annotation'] = bundle.obj.annotation()
            bundle.data['url'] = bundle.obj.get_absolute_url()

            modified = bundle.obj.modified.strftime("%m/%d/%y %I:%M %p") \
                if bundle.obj.modified else ''

            bundle.data['metadata'] = {
                'tags': TagResource().render_list(bundle.request,
                                                  bundle.obj.tags_split()),
                'body': bundle.obj.body.strip() if bundle.obj.body else '',
                'primary_type': bundle.obj.asset.primary.label,
                'modified': modified,
                'timecode': bundle.obj.range_as_timecode(),
                'title': bundle.obj.title
            }

            editable = (bundle.request.user.id ==
                        getattr(bundle.obj, 'author_id', -1))
            citable = bundle.request.GET.get('citable', '') == 'true'

            # assumed: there is only one ProjectNote per annotation
            reference = ProjectNote.objects.filter(
                annotation__id=bundle.obj.id).first()
            if reference:
                # notes in a submitted response are not editable
                editable = editable and not reference.project.is_submitted()

                if citable:
                    # this is a heavy operation. don't call it unless needed
                    citable = reference.project.can_cite(bundle.request.course,
                                                         bundle.request.user)

            bundle.data['editable'] = editable
            bundle.data['citable'] = citable

            termResource = TermResource()
            vocabulary = {}
            related = TermRelationship.objects.get_for_object(
                bundle.obj).select_related('term__vocabulary')
            for rel in related:
                if rel.term.vocabulary.id not in vocabulary:
                    vocabulary[rel.term.vocabulary.id] = {
                        'id': rel.term.vocabulary.id,
                        'display_name': rel.term.vocabulary.display_name,
                        'terms': []
                    }
                vocabulary[rel.term.vocabulary.id]['terms'].append(
                    termResource.render_one(bundle.request, rel.term))
            bundle.data['vocabulary'] = vocabulary.values()
        except Asset.DoesNotExist:
            bundle.data['asset_id'] = ''
            bundle.data['metadata'] = {'title': 'Item Deleted'}
        return bundle

    def render_one(self, request, selection, asset_key):
        # assumes user is allowed to see this note
        bundle = self.build_bundle(obj=selection, request=request)
        dehydrated = self.full_dehydrate(bundle)
        bundle.data['asset_key'] = '%s_%s' % (asset_key,
                                              bundle.data['asset_id'])
        return self._meta.serializer.to_simple(dehydrated, None)


class DiscussionIndexResource(object):

    def render_list(self, request, indicies):
        collaborations = DiscussionIndex.with_permission(request, indicies)

        ctx = {
            'references': [{
                'id': obj.collaboration.object_pk,
                'title': obj.collaboration.title,
                'type': obj.get_type_label(),
                'url': obj.get_absolute_url(),
                'modified': obj.modified.strftime("%m/%d/%y %I:%M %p")}
                for obj in collaborations]}

        return ctx
