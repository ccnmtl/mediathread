from django import template
from djangosherd.models import SherdNote

from djangohelpers.templatetags import TemplateTagNode

from django.db.models import get_model
Comment = get_model('comments','comment')

class GetAnnotations(TemplateTagNode):

    noun_for = {"by":"author", "on":"asset"}

    def __init__(self, varname, author, asset):
        TemplateTagNode.__init__(self, varname, author=author, asset=asset)

    def execute_query(self, author, asset):
        return SherdNote.objects.filter(author=author, asset=asset)

class GetAllAnnotations(TemplateTagNode):

    noun_for = {"on":"asset"}

    def __init__(self, varname, asset):
        TemplateTagNode.__init__(self, varname, asset=asset)

    def execute_query(self, asset):
        return SherdNote.objects.filter(asset=asset)

class GetGlobalAnnotation(GetAnnotations):
    def execute_query(self, author, asset):
        annotation, created = SherdNote.objects.global_annotation(asset, author)
        return annotation

import re
def striptags_better(value):
    text = value.comment if isinstance(value, Comment) else unicode(value)
    parts = re.split('\<\/?[a-zA-Z]+[^>]*>',text)
    return ''.join(parts)

register = template.Library()
register.tag('get_annotations', GetAnnotations.process_tag)
register.tag('get_all_annotations', GetAllAnnotations.process_tag)
register.tag('get_global_annotation', GetGlobalAnnotation.process_tag)

register.filter('striptags_better',striptags_better)
