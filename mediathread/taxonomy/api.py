#pylint: disable-msg=R0904
from courseaffils.models import Course
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from mediathread.api import ClassLevelAuthentication, FacultyAuthorization
from mediathread.taxonomy.models import Vocabulary, Term, TermRelationship
from tastypie.fields import ToManyField
from tastypie.resources import ModelResource
from tastypie.validation import Validation


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

    def read_list(self, object_list, bundle):
        request = bundle.request

        course_type = ContentType.objects.get_for_model(request.course)
        object_list = object_list.filter(content_type=course_type,
                                         object_id=request.course.id)

        return object_list.order_by('id')


class VocabularyResource(ModelResource):
    term_set = ToManyField(
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
        ordering = ['display_name']
        validation = VocabularyValidation()

    def alter_list_data_to_serialize(self, request, to_be_serialized):
        to_be_serialized['objects'] = sorted(
            to_be_serialized['objects'],
            key=lambda bundle: bundle.data['display_name'])
        return to_be_serialized

    def dehydrate(self, bundle):
        bundle.data['content_type_id'] = bundle.obj.content_type.id
        return bundle

    def hydrate(self, bundle):
        bundle.obj.content_type = ContentType.objects.get(
            id=bundle.data['content_type_id'])
        bundle.obj.course = Course.objects.get(id=bundle.data['object_id'])
        return bundle

    def render_one(self, request, vocabulary):
        bundle = self.build_bundle(obj=vocabulary, request=request)
        dehydrated = self.full_dehydrate(bundle)
        return self._meta.serializer.to_simple(dehydrated, None)

    def render_list(self, request, vocabularies):
        data = []
        for vocabulary in vocabularies:
            data.append(self.render_one(request, vocabulary))
        return data

    def render_related(self, request, object_list):
        if len(object_list) < 1:
            return []

        ctx = {}
        term_resource = TermResource()

        related = TermRelationship.objects.get_for_object_list(object_list)
        term_counts = related.values('term').annotate(count=Count('id'))

        for rel in related:
            if rel.term.vocabulary.id not in ctx:
                vocab_ctx = {'id': rel.term.vocabulary.id,
                             'display_name': rel.term.vocabulary.display_name,
                             'term_set': [],
                             'terms': []}
                ctx[rel.term.vocabulary.id] = vocab_ctx

            # have we seen this term before?
            try:
                ctx[rel.term.vocabulary.id]['terms'].index(rel.term.id)
            except ValueError:
                the_term = term_resource.render_one(request, rel.term)
                the_term['count'] = term_counts.get(term=rel.term.id)['count']
                ctx[rel.term.vocabulary.id]['term_set'].append(the_term)
                ctx[rel.term.vocabulary.id]['terms'].append(rel.term.id)

        values = ctx.values()
        values.sort(lambda a, b: cmp(a['display_name'].lower(),
                    b['display_name'].lower()))

        return values
