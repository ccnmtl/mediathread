from django.conf.urls import include, patterns, url
from .views import *

urlpatterns = patterns('',
    url(r'^invite-students/$',
        invite_students,
        name="invite-students"),
    url(r'^registration_form/$',
        registration_form,
        name='registration-form'),
    (r'', include('allauth.urls'))
)
