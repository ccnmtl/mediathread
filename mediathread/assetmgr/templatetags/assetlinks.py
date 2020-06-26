from django import template
from mediathread.assetmgr.models import ExternalCollection

register = template.Library()


@register.filter
def source_url(source, request):
    return source.url_processed(request)


@register.simple_tag
def map_course_collection(course, suggested_collection):
    return ExternalCollection.objects.filter(
        title=suggested_collection.title, course=course).first()
