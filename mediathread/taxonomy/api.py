#pylint: disable-msg=R0904
from courseaffils.models import Course
from django.contrib.contenttypes.models import ContentType
from django.db.models.aggregates import Count
from mediathread.api import ClassLevelAuthentication, ToManyFieldEx, \
    FacultyAuthorization, RestrictedCourseResource
from mediathread.djangosherd.models import SherdNote
from mediathread.taxonomy.models import Vocabulary, Term, TermRelationship
from tastypie.resources import ModelResource
from tastypie.validation import Validation


class TermRelationshipResource(RestrictedCourseResource):
    def __init__(self, course=None):
        super(TermRelationshipResource, self).__init__(None)
        self.filters = {}

    class Meta:
        queryset = TermRelationship.objects.none()
        authentication = ClassLevelAuthentication()
        limit = 1000
        max_limit = 1000

    def _filter_terms(self, request, note_set):
        if 'assets' in self.filters:
            note_set = note_set.filter(asset__id__in=self.filters['assets'])

        related = TermRelationship.objects.filter(
            term__vocabulary__id=self.filters['vocabulary'],
            content_type=ContentType.objects.get_for_model(SherdNote),
            object_id__in=[n.id for n in note_set])

        terms = list(related.values('term__id',
                                    'term__vocabulary__id',
                                    'term__display_name').annotate(
            count=Count('term__id')))

        terms.sort(lambda a, b: cmp(a['term__display_name'].lower(),
                                    b['term__display_name'].lower()))
        return terms

    def get_unrestricted(self, request, object_list, course):
        notes = SherdNote.objects.filter(asset__course=course)
        return self._filter_terms(request, notes)

    def get_restricted(self, request, object_list, course):
        whitelist = [f.id for f in course.faculty]
        whitelist.append(request.user.id)

        notes = SherdNote.objects.filter(asset__course=course,
                                         author__id__in=whitelist)
        return self._filter_terms(request, notes)

    def filter(self, request, filters):
        self.filters = filters
        objects = self.obj_get_list(request=request)

        last = len(objects) - 1
        for idx, term in enumerate(objects):
            term['last'] = idx == last

        return objects


class TermValidation(Validation):
    def is_valid(self, bundle, request=None):
        errors = {}

        a = Term.objects.filter(
            display_name=bundle.data['display_name'],
            vocabulary_id=bundle.data['vocabulary_id'])

        if len(a) > 0:  # vocabulary exists with this name
            if not 'pk' in bundle.data or a[0].pk != int(bundle.data['pk']):
                # a vocabulary already exists with this name
                msg = 'A %s term already exists. Please choose another name' \
                    % bundle.data['display_name']
                errors['error_message'] = [msg]
        return errors


class TermResource(ModelResource):

    class Meta:
        queryset = Term.objects.all().order_by('id')
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'put', 'delete']
        authentication = ClassLevelAuthentication()
        authorization = FacultyAuthorization()
        excludes = ['description', 'ordinality']
        validation = TermValidation()

    def dehydrate(self, bundle):
        bundle.data['vocabulary_id'] = bundle.obj.vocabulary.id
        if hasattr(bundle.obj, "count"):
            bundle.data['count'] = int(bundle.obj.count)
        return bundle

    def hydrate(self, bundle):
        bundle.obj.vocabulary = Vocabulary.objects.get(
            id=bundle.data['vocabulary_id'])
        return bundle

    def render_one(self, request, term):
        bundle = self.build_bundle(obj=term, request=request)
        dehydrated = self.full_dehydrate(bundle)
        return self._meta.serializer.to_simple(dehydrated, None)


class VocabularyValidation(Validation):
    def is_valid(self, bundle, request=None):
        errors = {}

        a = Vocabulary.objects.filter(
            content_type_id=bundle.data['content_type_id'],
            display_name=bundle.data['display_name'],
            object_id=bundle.data['object_id'])

        if len(a) > 0:  # vocabulary exists with this name
            if not 'pk' in bundle.data or a[0].pk != int(bundle.data['pk']):
                # a vocabulary already exists with this name
                msg = 'A %s concept exists. Please choose another name' \
                    % bundle.data['display_name']
                errors['error_message'] = [msg]
        return errors


class VocabularyAuthorization(FacultyAuthorization):

    def apply_limits(self, request, object_list):
        '''Limit vocabulary list to the current course'''
        course_type = ContentType.objects.get_for_model(request.course)
        invisible = []
        for vocabulary in object_list:
            if (vocabulary.content_type == course_type and
                    not vocabulary.content_object == request.course):
                invisible.append(vocabulary.id)

        object_list = object_list.exclude(id__in=invisible)
        return object_list.order_by('id')


class VocabularyResource(ModelResource):
    term_set = ToManyFieldEx(
        'mediathread.taxonomy.api.TermResource',
        'term_set',
        blank=True, null=True, full=True, readonly=True)

    class Meta:
        queryset = Vocabulary.objects.all().order_by('id')
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'put', 'delete']
        authentication = ClassLevelAuthentication()
        authorization = VocabularyAuthorization()
        excludes = ['description', 'single_select']
        ordering = ['id', 'title']
        validation = VocabularyValidation()

    def dehydrate(self, bundle):
        bundle.data['content_type_id'] = bundle.obj.content_type.id
        return bundle

    def hydrate(self, bundle):
        bundle.obj.content_type = ContentType.objects.get(
            id=bundle.data['content_type_id'])
        bundle.obj.course = Course.objects.get(id=bundle.data['object_id'])
        return bundle

    def render_one(self, request, v):
        bundle = self.build_bundle(obj=v, request=request)
        dehydrated = self.full_dehydrate(bundle)
        return self._meta.serializer.to_simple(dehydrated, None)

    def render_list(self, request, vocabulary):
        data = []
        for v in vocabulary:
            data.append(self.render_one(request, v))
        return data
