from django.conf.urls import include, patterns, url
from .views import *

urlpatterns = patterns('',
    url(r'create/$', course_create, name='course_create')
)
