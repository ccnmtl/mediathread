from django.conf.urls import include, patterns, url
from .views import invite_students

urlpatterns = patterns('',
    url(r'invite-students/$',
        invite_students,
        name="invite-students"),
    (r'', include('allauth.urls'))
)
