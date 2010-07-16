from django import template
from djangosherd.models import SherdNote
import re
from djangohelpers.templatetags import TemplateTagNode

from django.db.models import get_model
Comment = get_model('comments','comment')

filter_by = {
    'tag': lambda note, tag: re.search(r'\b%s\b'%tag, note.tags),
    'added': SherdNote.date_filter_for('added'),
    'modified': SherdNote.date_filter_for('modified'),
}

class GetAnnotations(TemplateTagNode):

    noun_for = {"filter":"filters", "by":"author", "on":"asset", }

    def __init__(self, varname, author, asset, filters):
        TemplateTagNode.__init__(self, varname, author=author, asset=asset, filters=filters)

    def execute_query(self, author, asset, filters):
        notes = None
        if author is False:
            notes = SherdNote.objects.filter(asset=asset)
        elif author:
            notes = SherdNote.objects.filter(author=author, asset=asset)
        if notes and filters:
            for f,v in filters.items():
                #don't filter global annotations out
                notes = [n for n in notes
                         if n.is_null() or filter_by[f](n,v)]
        return notes

class GetAllAnnotations(TemplateTagNode):

    noun_for = {"on":"asset"}

    def __init__(self, varname, asset):
        TemplateTagNode.__init__(self, varname, asset=asset)

    def execute_query(self, asset):
        return SherdNote.objects.filter(asset=asset)

class GetGlobalAnnotation(GetAnnotations):
    noun_for = {"by":"author", "on":"asset", }
    def __init__(self, varname, author, asset):
        TemplateTagNode.__init__(self, varname, author=author, asset=asset)
    def execute_query(self, author, asset):
        annotation, created = SherdNote.objects.global_annotation(asset, author, auto_create=False)
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

def dictify(arry):
    return dict(arry)
register.filter('dictify', dictify)
