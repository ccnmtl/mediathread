from django.urls import path

from lti_auth.views import LTIConfigView, LTILandingPage, LTIRoutingView, \
    LTICourseEnableView


urlpatterns = [
    path('config.xml', LTIConfigView.as_view(), {}, 'lti-config'),
    path('enable/', LTICourseEnableView.as_view(), {}, 'lti-enable-course'),
    path('landing/<slug:context>/',
         LTILandingPage.as_view(), {}, 'lti-landing-page'),
    path('', LTIRoutingView.as_view(), {}, 'lti-login'),
]
