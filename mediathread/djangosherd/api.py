from django.db.models.query_utils import Q
from mediathread.api import UserResource, ClassLevelAuthentication, TagResource
from mediathread.assetmgr.models import Asset
from mediathread.djangosherd.models import SherdNote
from mediathread.main import course_details
from mediathread.main.course_details import cached_course_is_member, \
    cached_course_is_faculty
from mediathread.taxonomy.api import TermResource
from mediathread.taxonomy.models import TermRelationship
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.resources import ModelResource


class SherdNoteAuthorization(Authorization):

    def apply_limits(self, request, object_list, exclude_global=True):
        if request.user.is_authenticated():
            if exclude_global:
                # only request user's global annotations
                object_list = object_list.exclude(~Q(author=request.user),
                                                  range1__isnull=True)

            # Make sure the requesting user is allowed to see this note
            invisible = []
            courses = {}
            for note in object_list.select_related('asset__course'):
                course = note.asset.course

                # Cache this out per course/user. It's just too slow otherwise
                if not course.id in courses.keys():
                    courses[course.id] = {'whitelist': None}
                    is_faculty = cached_course_is_faculty(course, request.user)
                    if (not course_details.all_selections_are_visible(course)
                            and not is_faculty):
                        courses[course.id]['whitelist'] = list(course.faculty)
                        courses[course.id]['whitelist'].append(request.user)

                if not cached_course_is_member(course, request.user):
                    invisible.append(note.id)
                elif (courses[course.id]['whitelist'] and
                        not note.author in courses[course.id]['whitelist']):
                    # apply per course limitations
                    # the user or a faculty member must be the selection author
                    invisible.append(note.id)

            return object_list.exclude(id__in=invisible).order_by('id')
        elif request.public:
            # attribute "public" set on request when requesting a
            # public_to_world essay. all notes are public by default
            return object_list.order_by('id')
        else:
            return []


class SherdNoteResource(ModelResource):
    author = fields.ForeignKey(UserResource, 'author',
                               full=True, null=True, blank=True)

    class Meta:
        queryset = SherdNote.objects.select_related('asset').order_by("id")
        excludes = ['tags', 'body', 'added', 'modified']
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        filtering = {
            'author': ALL_WITH_RELATIONS,
            'range1': ALL_WITH_RELATIONS,
        }

        # User is logged into some course
        authentication = ClassLevelAuthentication()

        # User is authorized to look at this particular SherdNote
        authorization = SherdNoteAuthorization()

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

            bundle.data['editable'] = (bundle.request.user.id ==
                                       getattr(bundle.obj, 'author_id', -1))

            if bundle.request.GET.get('citable', '') == 'true':
                bundle.data['citable'] = True

            vocabulary = {}
            related = list(TermRelationship.objects.get_for_object(bundle.obj))
            for r in related:
                if r.term.vocabulary.id not in vocabulary:
                    vocabulary[r.term.vocabulary.id] = {
                        'id': r.term.vocabulary.id,
                        'display_name': r.term.vocabulary.display_name,
                        'terms': []
                    }
                vocabulary[r.term.vocabulary.id]['terms'].append(
                    TermResource().render_one(bundle.request, r.term))
            bundle.data['vocabulary'] = [val for k, val in vocabulary.items()]
        except Asset.DoesNotExist:
            bundle.data['asset_id'] = ''
            bundle.data['metadata'] = {'title': 'Item Deleted'}
        return bundle

    def render_one(self, request, selection, asset_key):
        bundle = self.build_bundle(obj=selection, request=request)
        dehydrated = self.full_dehydrate(bundle)
        bundle.data['asset_key'] = '%s_%s' % (asset_key,
                                              bundle.data['asset_id'])
        return self._meta.serializer.to_simple(dehydrated, None)

    def render_list(self, request, lst, asset_key):
        data = []
        for item in lst:
            bundle = self.build_bundle(obj=item, request=request)
            bundle.data['asset_key'] = '%s_%s' % (
                asset_key, bundle.obj.asset.id)
            dehydrated = self.full_dehydrate(bundle)
            data.append(dehydrated.data)
        return data


class SherdNoteSummaryResource(ModelResource):
    author = fields.ForeignKey(UserResource, 'author', full=True)

    class Meta:
        queryset = SherdNote.objects.none()
        excludes = ['tags', 'body', 'added', 'modified', 'title']

        # User is logged into some course
        authentication = ClassLevelAuthentication()

        # User is authorized to look at this particular SherdNote
        authorization = SherdNoteAuthorization()

    def dehydrate(self, bundle):
        bundle.data['is_global_annotation'] = bundle.obj.is_global_annotation()
        return bundle
