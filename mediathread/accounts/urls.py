from django.conf.urls import include, patterns, url
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import password_change
from .views import *

urlpatterns = patterns('',
    url(r'^set_password/$',
        password_change, {
            'password_change_form': SetPasswordForm,
            'post_change_redirect': '/'
        },
        name="set_password"),
    url(r'^invite_students/$',
        invite_students,
        name="invite-students"),
    url(r'^registration_form/$',
        registration_form,
        name='registration-form'),
    (r'', include('allauth.urls'))
)
