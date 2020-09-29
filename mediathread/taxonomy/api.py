# pylint: disable-msg=R0904
from django.db.models import Count
from tastypie.fields import ToManyField
from tastypie.resources import ModelResource
from tastypie.validation import Validation

from mediathread.api import ClassLevelAuthentication, FacultyAuthorization
from mediathread.taxonomy.models import Vocabulary, Term, TermRelationship


class TermResource(ModelResource):

    class Meta:
        queryset = Term.objects.all().order_by('id')
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'put', 'delete']
        authentication = ClassLevelAuthentication()
        authorization = FacultyAuthorization()
        excludes = ['description', 'ordinality']
        always_return_data = True

    def hydrate(self, bundle):
        if 'vocabulary' in bundle.data:
            bundle.obj.vocabulary = VocabularyResource().get_via_uri(
                bundle.data['vocabulary'])
        elif (hasattr(bundle, 'related_obj') and
              bundle.related_obj is not None):
            bundle.obj.vocabulary = bundle.related_obj

        bundle.obj.display_name = bundle.data['display_name']
        return bundle

    def render_one(self, request, term):
        bundle = self.build_bundle(obj=term, request=request)
        dehydrated = self.full_dehydrate(bundle)
        return self._meta.serializer.to_simple(dehydrated, None)


class VocabularyValidation(Validation):
    def is_valid(self, bundle, request=None):
        errors = {}

        a = Vocabulary.objects.filter(
            display_name=bundle.data['display_name'],
            course=bundle.request.course)

        if len(a) > 0:  # vocabulary exists with this name
            if not bundle.obj or not bundle.obj.pk or a[0].pk != bundle.obj.pk:
                # a vocabulary already exists with this name
                msg = 'A %s concept exists. Please choose another name' \
                    % bundle.data['display_name']
                errors['error_message'] = [msg]
        return errors


class VocabularyAuthorization(FacultyAuthorization):

    def read_list(self, object_list, bundle):
        request = bundle.request
        return object_list.filter(course=request.course)


class VocabularyResource(ModelResource):
    term_set = ToManyField(
        'mediathread.taxonomy.api.TermResource',
        'term_set',
        blank=True, null=True, full=True, readonly=False,
        related_name='vocabulary')

    class Meta:
        queryset = Vocabulary.objects.all().order_by('id')
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'put', 'delete']
        authentication = ClassLevelAuthentication()
        authorization = VocabularyAuthorization()
        excludes = ['description', 'single_select']
        ordering = ['display_name']
        validation = VocabularyValidation()
        always_return_data = True

    def alter_list_data_to_serialize(self, request, to_be_serialized):
        to_be_serialized['objects'] = sorted(
            to_be_serialized['objects'],
            key=lambda bundle: bundle.data['display_name'])
        return to_be_serialized

    def hydrate(self, bundle):
        bundle.obj.course = bundle.request.course
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

        # render vocabulary and terms related to these notes
        ids = object_list.values_list('id', flat=True)
        related = TermRelationship.objects.filter(sherdnote__id__in=ids)
        term_counts = related.values('term').annotate(count=Count('id'))
        related = related.select_related('term__vocabulary')

        for rel in related:
            if rel.term.vocabulary.id not in ctx:
                vocab_ctx = {'id': rel.term.vocabulary.id,
                             'vocabulary_id': rel.term.vocabulary.id,
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
        return sorted(values, key=lambda x: x.get('display_name').lower())

    def render_for_course(self, request, object_list):
        related = TermRelationship.objects.none()
        if len(object_list) > 0:
            ids = [obj.id for obj in object_list]
            related = TermRelationship.objects.filter(sherdnote__id__in=ids)

        data = []
        for vocabulary in Vocabulary.objects.filter(course=request.course):
            ctx = self.render_one(request, vocabulary)
            for term in ctx['term_set']:
                term['count'] = related.filter(term__id=term['id']).count()
            data.append(ctx)

        return sorted(data, key=lambda x: x.get('display_name').lower())
