from django.conf.urls.defaults import *
from django.conf import settings
import os.path

media_root = os.path.join(os.path.dirname(__file__),"media")

urlpatterns = patterns(
    'djangosherd.views',

    url(r'^(?P<username>\w+)/$', 
        'annotations_collection_fragment', name="annotations-fragment"),

    )
