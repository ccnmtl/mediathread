from django import forms
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.defaultfilters import slugify


class GenericRelationshipManager(models.Manager):
    def get_for_object(self, obj):
        ctype = ContentType.objects.get_for_model(obj)
        return self.filter(content_type__pk=ctype.pk, object_id=obj.pk)

    def get_for_object_list(self, object_list):
        ctype = ContentType.objects.get_for_model(object_list[0])
        ids = object_list.values_list('id', flat=True)
        return self.filter(content_type__pk=ctype.pk, object_id__in=ids)


class Vocabulary(models.Model):
    name = models.SlugField(max_length=100)
    display_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    single_select = models.BooleanField(default=False)
    onomy_url = models.TextField(null=True, blank=True)
    skos_uid = models.CharField(null=True, blank=True, max_length=100)
    # Map this taxonomy to something else. like a course.
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    objects = GenericRelationshipManager()

    class Meta:
        ordering = ['display_name', 'id']

    def save(self, force_insert=False, force_update=False):
        self.name = slugify(self.display_name)
        super(Vocabulary, self).save(force_insert, force_update)

    def __unicode__(self):
        return self.display_name


class VocabularyForm(forms.ModelForm):
    class Meta:
        model = Vocabulary


class Term(models.Model):
    name = models.SlugField(max_length=100)
    vocabulary = models.ForeignKey(Vocabulary)
    display_name = models.CharField(max_length=100)
    description = models.CharField(null=True, blank=True, max_length=256)
    ordinality = models.IntegerField(null=True, blank=True, default=0)
    skos_uid = models.CharField(null=True, blank=True, max_length=100)

    class Meta:
        unique_together = ('name', 'vocabulary')
        ordering = ['display_name', 'id']

    def __unicode__(self):
        return "%s, %s" % (self.vocabulary, self.display_name)

    def save(self, force_insert=False, force_update=False):
        self.name = slugify(self.display_name)
        super(Term, self).save(force_insert, force_update)

    def to_json(self):
        return {
            'id': self.id,
            'display_name': self.display_name,
            'description': self.description
        }


class TermForm(forms.ModelForm):
    class Meta:
        model = Term


class TermRelationship(models.Model):
    term = models.ForeignKey(Term)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    objects = GenericRelationshipManager()

    class Meta:
        unique_together = ('term', 'content_type', 'object_id')
        ordering = ['term__display_name', 'id']
