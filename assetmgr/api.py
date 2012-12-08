from tastypie import fields
from tastypie.resources import ModelResource
from mediathread.api import ClassLevelAuthentication, UserResource
from tastypie.authorization import Authorization
from assetmgr.models import Asset
from djangosherd.api import SherdNoteAuthorization
from djangosherd.models import SherdNote


class AssetAuthorization(Authorization):

    def apply_limits(self, request, object_list, course=None):
        # HACK: Tastypie does not call apply_limits on m2m relationships
        # Course is calling apply_limits manually + specifying its course
        if course is None:
            course = request.course
        elif not course.is_member(request.user):
            return SherdNote.objects.none()

        # filter by course
        object_list = object_list.filter(course=course)
        return object_list


class AssetResource(ModelResource):
    author = fields.ForeignKey(UserResource, 'author', full=True)

    selections = fields.ToManyField(
        'djangosherd.api.SherdNoteResource', blank=True, null=True, full=True,
        attribute=lambda bundle: SherdNoteAuthorization().apply_limits(
        bundle.request, bundle.obj.sherdnote_set.all(), bundle.obj.course).
        order_by('id'))

    class Meta:
        queryset = Asset.objects.all().order_by('id')
        excludes = ['added', 'modified', 'course', 'active', 'metadata_blob']
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        authentication = ClassLevelAuthentication()
        authorization = AssetAuthorization()

    def dehydrate(self, bundle):
        bundle.data['thumb_url'] = bundle.obj.thumb_url
        bundle.data['primary_type'] = bundle.obj.primary.label
        return bundle
