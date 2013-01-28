from assetmgr.models import Asset
from mediathread.api import ClassLevelAuthentication, UserResource
from mediathread.api import ToManyFieldEx
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.resources import ModelResource


class AssetAuthorization(Authorization):

    def apply_limits(self, request, object_list):

        invisible = []
        for asset in object_list:
            if not asset.course.is_member(request.user):
                invisible.append(asset.id)

        object_list = object_list.exclude(id__in=invisible)
        return object_list.order_by('id')


class AssetResource(ModelResource):
    author = fields.ForeignKey(UserResource, 'author', full=True)

    sherdnote_set = ToManyFieldEx(
        'djangosherd.api.SherdNoteResource',
        'sherdnote_set',
        blank=True, null=True, full=True)

        # lambda bundle: SherdNoteAuthorization().apply_limits(
        # bundle.request, bundle.obj.sherdnote_set.all(), bundle.obj.course).
        # order_by('id'))

    class Meta:
        queryset = Asset.objects.all().order_by('id')
        excludes = ['added', 'modified', 'course', 'active', 'metadata_blob']
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        authentication = ClassLevelAuthentication()
        authorization = AssetAuthorization()

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
        return bundle
