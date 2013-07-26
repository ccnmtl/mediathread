from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    url(r'^invite-students/$',
        'invite_students',
        name="invite-students"),
)
