from django.contrib.contenttypes.models import ContentType
from mediathread.api import UserResource, ClassLevelAuthentication, TagResource
from mediathread.djangosherd.models import SherdNote
from mediathread.main import course_details
from mediathread.taxonomy.api import VocabularyResource
from mediathread.taxonomy.models import Vocabulary, TermRelationship
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.resources import ModelResource


class SherdNoteAuthorization(Authorization):

    def apply_limits(self, request, object_list):
        if request.user.is_authenticated():
            object_list = object_list.exclude(range1__isnull=True)

            # Make sure the requesting user is allowed to see this note
            invisible = []
            for note in object_list:
                course = note.asset.course

                if not course.is_member(request.user):
                    invisible.append(note.id)
                elif (not course.is_faculty(request.user) and
                      not course_details.all_selections_are_visible(course)):
                    # apply per course limitations
                    # the user or a faculty member must be the selection author
                    authorized = list(course.faculty)
                    authorized.append(request.user)
                    if not note.author in authorized:
                        invisible.append(note.id)

            return object_list.exclude(id__in=invisible).order_by('id')
        elif request.public:
            # attribute "public" set on request when requesting a
            # public_to_world essay. all notes are public by default
            return object_list.order_by('id')
        else:
            return []


class SherdNoteResource(ModelResource):
    author = fields.ForeignKey(UserResource, 'author', full=True)

    class Meta:
        queryset = SherdNote.objects.all().order_by("id")
        excludes = ['tags', 'body', 'added', 'modified']
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        filtering = {'author': ALL_WITH_RELATIONS}

        # User is logged into some course
        authentication = ClassLevelAuthentication()

        # User is authorized to look at this particular SherdNote
        authorization = SherdNoteAuthorization()

    def dehydrate(self, bundle):
        bundle.data['asset_id'] = str(bundle.obj.asset.id)
        bundle.data['is_global_annotation'] = \
            bundle.obj.is_global_annotation()
        bundle.data['is_null'] = bundle.obj.is_null()
        bundle.data['annotation'] = bundle.obj.annotation()

        # todo - remove the request reliance here
        bundle.data['editable'] = (bundle.request.user.id ==
                                   getattr(bundle.obj, 'author_id', -1))

        if bundle.request.GET.get('citable', '') == 'true':
            bundle.data['citable'] = True

        bundle.data['url'] = bundle.obj.get_absolute_url()

        concepts = Vocabulary.objects.get_for_object(bundle.request.course)

        note_type = ContentType.objects.get_for_model(bundle.obj)
        bundle.data['concepts'] = []
        for concept in concepts:
            if len(concept.term_set.all()) > 0:
                the_json = VocabularyResource().render_one(bundle.request,
                                                           concept)
                lst = list(TermRelationship.objects.filter(
                    content_type=note_type, object_id=bundle.obj.id,
                    term__vocabulary__id=concept.id))

                if len(lst) > 0:
                    the_json['selected'] = ''
                    for r in lst[:-1]:
                        the_json['selected'] += r.term.display_name + ', '
                    else:
                        the_json['selected'] += lst[-1].term.display_name

                bundle.data['concepts'].append(the_json)

        bundle.data['metadata'] = {
            'tags': TagResource().render_list(bundle.request,
                                              bundle.obj.tags_split()),
            'body': bundle.obj.body.strip() if bundle.obj.body else '',
            'primary_type': bundle.obj.asset.primary.label,
            'modified': bundle.obj.modified.strftime("%m/%d/%y %I:%M %p"),
            'timecode': bundle.obj.range_as_timecode(),
            'title': bundle.obj.title
        }
        return bundle

    def render_one(self, request, selection, asset_key):
        bundle = self.build_bundle(obj=selection, request=request)
        dehydrated = self.full_dehydrate(bundle)
        bundle.data['asset_key'] = '%s_%s' % (asset_key, bundle.obj.asset.id)
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
