from courseaffils.models import Course
from django.contrib.contenttypes.models import ContentType
from mediathread.api import ClassLevelAuthentication, ToManyFieldEx, \
    FacultyAuthorization
from mediathread.taxonomy.models import Vocabulary, Term
from tastypie.resources import ModelResource


class TermResource(ModelResource):

    class Meta:
        queryset = Term.objects.all().order_by('id')
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'put', 'delete']
        authentication = ClassLevelAuthentication()
        authorization = FacultyAuthorization()
        excludes = ['description', 'ordinality']

    def dehydrate(self, bundle):
        bundle.data['vocabulary_id'] = bundle.obj.vocabulary.id
        return bundle

    def hydrate(self, bundle):
        bundle.obj.vocabulary = Vocabulary.objects.get(
            id=bundle.data['vocabulary_id'])
        return bundle


class VocabularyAuthorization(FacultyAuthorization):

    def apply_limits(self, request, object_list):
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

    def dehydrate(self, bundle):
        bundle.data['content_type_id'] = bundle.obj.content_type.id
        return bundle

    def hydrate(self, bundle):
        bundle.obj.content_type = ContentType.objects.get(
            id=bundle.data['content_type_id'])
        bundle.obj.course = Course.objects.get(id=bundle.data['object_id'])
        return bundle

    def render_one(self, request, item):
        bundle = self.build_bundle(obj=item, request=request)
        dehydrated = self.full_dehydrate(bundle)
        return self._meta.serializer.to_simple(dehydrated, None)

    def render_list(self, request, lst):
        a = []
        for o in lst:
            if len(o.term_set.all()) > 0:
                the_json = self.render_one(request, o)
                a.append(the_json)
        return a
