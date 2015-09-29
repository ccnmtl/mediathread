from django.conf.urls import patterns, url

from lti_auth.views import LTILoginView, LTIConfigView, LTILandingPage


urlpatterns = patterns(
    '',
    url(r'^config.xml$', LTIConfigView.as_view(), {}, 'lti-config'),
    url(r'^landing/$', LTILandingPage.as_view(), {}, 'lti-landing-page'),
    url(r'^$', LTILoginView.as_view(), {}, 'lti-login'),
)
