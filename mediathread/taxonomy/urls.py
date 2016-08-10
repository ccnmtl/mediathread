from django.conf.urls import url
import os.path

from .views import taxonomy_workspace

media_root = os.path.join(os.path.dirname(__file__), "media")

urlpatterns = [
    url(r'^$',
        taxonomy_workspace,
        name='taxonomy-workspace'),

    url(r'^/(?P<vocabulary_id>\d+)/$',
        taxonomy_workspace,
        name='taxonomy-workspace-view')
]
