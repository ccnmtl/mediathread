from django.conf.urls import patterns, url

from lti_auth.views import LTILoginView, LTIConfigView


urlpatterns = patterns(
    '',
    url(r'^config/$', LTIConfigView.as_view(), {}, 'lti-config'),
    url(r'^$', LTILoginView.as_view(), {}, 'lti-login'),
)
