from assetmgr.models import Asset,Source

from django import template

#from djangohelpers.templatetags import Node

def source_url(source,request):
        return source.url_processed(request)

register = template.Library()
register.filter(source_url)
