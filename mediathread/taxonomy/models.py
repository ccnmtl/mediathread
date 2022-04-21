from courseaffils.models import Course
from django import forms
from django.db import models
from django.template.defaultfilters import slugify

from mediathread.djangosherd.models import SherdNote


class Vocabulary(models.Model):
    name = models.SlugField(max_length=100)
    display_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    single_select = models.BooleanField(default=False)
    onomy_url = models.TextField(null=True, blank=True)
    skos_uri = models.CharField(null=True, blank=True, max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        ordering = ['display_name', 'id']

    def save(self, force_insert=False, force_update=False):
        self.name = slugify(self.display_name)
        super(Vocabulary, self).save(force_insert, force_update)

    def __str__(self):
        return self.display_name


class VocabularyForm(forms.ModelForm):
    class Meta:
        model = Vocabulary
        exclude = []


class Term(models.Model):
    name = models.SlugField(max_length=100)
    vocabulary = models.ForeignKey(Vocabulary, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100)
    description = models.CharField(null=True, blank=True, max_length=256)
    ordinality = models.IntegerField(null=True, blank=True, default=0)
    skos_uri = models.CharField(null=True, blank=True, max_length=100)

    class Meta:
        unique_together = ('name', 'vocabulary')
        ordering = ['display_name', 'id']

    def __str__(self):
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
        exclude = []


class TermRelationship(models.Model):
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    sherdnote = models.ForeignKey(SherdNote, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('term', 'sherdnote')
        ordering = ['term__display_name', 'id']
