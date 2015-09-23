from django.conf.urls import patterns, url

from lti_auth.views import LTILoginView

urlpatterns = patterns(
    '',
    url(r'^$', LTILoginView.as_view(), {}, 'lti-login'),
)
