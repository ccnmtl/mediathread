from django.urls import path
import os.path

from .views import taxonomy_workspace

media_root = os.path.join(os.path.dirname(__file__), "media")

urlpatterns = [
    path('',
         taxonomy_workspace,
         name='taxonomy-workspace'),

    path('<int:vocabulary_id>/',
         taxonomy_workspace,
         name='taxonomy-workspace-view')
]
