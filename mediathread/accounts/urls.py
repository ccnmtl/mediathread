from django.conf.urls.defaults import patterns, url
from .views import *

urlpatterns = patterns('',
    url(r'^invite-students/$',
        invite_students,
        name="invite-students"),
    url(r'^registration_form/$',
        registration_form,
        name='registration-form'),
)
