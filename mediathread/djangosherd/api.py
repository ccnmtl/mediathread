# pylint: disable-msg=R0904
from django.db.models.query_utils import Q
from django.urls import reverse
from mediathread.api import UserResource, TagResource
from mediathread.assetmgr.models import Asset
from mediathread.djangosherd.models import SherdNote, DiscussionIndex
from mediathread.sequence.models import SequenceAsset
from mediathread.taxonomy.api import TermResource
from tastypie import fields
from tastypie.resources import ModelResource


class SherdNoteResource(ModelResource):
    author = fields.ForeignKey(UserResource, 'author',
                               full=True, null=True, blank=True)

    class Meta:
        queryset = SherdNote.objects.select_related('asset')
        excludes = ['tags', 'body', 'added', 'modified']
        list_allowed_methods = []
        detail_allowed_methods = []

    def render_related_terms(self, bundle):
        termResource = TermResource()
        vocabulary = {}
        for rel in bundle.obj.termrelationship_set.all():
            if rel.term.vocabulary.id not in vocabulary:
                vocabulary[rel.term.vocabulary.id] = {
                    'id': rel.term.vocabulary.id,
                    'display_name': rel.term.vocabulary.display_name,
                    'terms': []
                }
            vocabulary[rel.term.vocabulary.id]['terms'].append(
                termResource.render_one(bundle.request, rel.term))
        return sorted(
            list(vocabulary.values()),
            key=lambda x: x.get('id'))

    def dehydrate(self, bundle):
        try:
            bundle.data['is_global_annotation'] = \
                bundle.obj.is_global_annotation
            bundle.data['asset_id'] = str(bundle.obj.asset.id)
            bundle.data['is_null'] = bundle.obj.is_null()
            bundle.data['annotation'] = bundle.obj.annotation()
            bundle.data['url'] = bundle.obj.get_absolute_url()
            bundle.data['local_url'] = reverse(
                'react_annotation_detail', kwargs={
                    'course_pk': bundle.obj.asset.course.pk,
                    'pk': bundle.obj.asset.pk,
                    'annotation_pk': bundle.obj.id
                })

            modified = bundle.obj.modified.strftime("%m/%d/%y %I:%M %p") \
                if bundle.obj.modified else ''

            bundle.data['metadata'] = {
                'tags': TagResource().render_list(bundle.request,
                                                  bundle.obj.tags_split()),
                'body': bundle.obj.body.strip() if bundle.obj.body else '',
                'primary_type': bundle.obj.asset.primary.label,
                'modified': modified,
                'title': bundle.obj.title
            }

            if bundle.obj.asset.media_type() == 'video':
                bundle.data['metadata']['timecode'] = \
                    bundle.obj.range_as_timecode()

            editable = (bundle.request.user.id ==
                        getattr(bundle.obj, 'author_id', -1))
            citable = bundle.request.GET.get('citable', '') == 'true'

            if self.in_selection_assignment_response(bundle.obj):
                # "first" here kills the prefetch/select_related optimization
                # use the qs array indexing to keep things fast
                reference = bundle.obj.projectnote_set.all()[0]

                editable = editable and not reference.project.is_submitted()

                # notes in a draft or submitted response may/may not be citable
                # based on its assignment visibility settings
                if citable:
                    # this is a heavy operation. don't call it unless needed
                    citable = reference.project.can_cite(bundle.request.course,
                                                         bundle.request.user)

            if self.in_sequence_assignment_response(bundle.obj):
                # notes in a submitted response are not editable
                editable = False

            bundle.data['editable'] = editable
            bundle.data['citable'] = citable
            bundle.data['vocabulary'] = self.render_related_terms(bundle)
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

    def in_selection_assignment_response(self, note):
        return note.projectnote_set.exists()

    def in_sequence_assignment_response(self, note):
        # For SequenceAssignmentResponses only
        # Do not allow editing or deleting when used as a primary video
        # or as a secondary media element
        return SequenceAsset.objects.filter(
            Q(projectsequenceasset__project__date_submitted__isnull=False),
            Q(spine=note) | Q(media_elements__media=note)).exists()


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
