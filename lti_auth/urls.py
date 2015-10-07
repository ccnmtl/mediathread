from django.conf.urls import patterns, url
from lti_auth.views import LTIConfigView, LTILandingPage, LTIRoutingView


urlpatterns = patterns(
    '',
    url(r'^config.xml$', LTIConfigView.as_view(), {}, 'lti-config'),
    url(r'^landing/$', LTILandingPage.as_view(), {}, 'lti-landing-page'),
    url(r'^$', LTIRoutingView.as_view(), {}, 'lti-login'),
)
