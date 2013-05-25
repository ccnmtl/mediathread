from mediathread.settings import *

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    #'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'mediathread_main.views.django_settings',
)

TEMPLATE_DIRS = (
    "/var/www/mediathread/mediathread/deploy_specific/templates",
    "/var/www/mediathread/mediathread/templates",
)

MEDIA_ROOT = '/var/www/mediathread/uploads/'

DEBUG = False
TEMPLATE_DEBUG = DEBUG

# IMPORTANT: make sure your local_settings.py file
# has a SENTRY_KEY defined
# as documented in the wiki
SENTRY_SITE = 'mediathread'
SENTRY_SERVERS = ['http://sentry.ccnmtl.columbia.edu/sentry/store/']

import logging
from sentry.client.handlers import SentryHandler
logger = logging.getLogger()
if SentryHandler not in map(lambda x: x.__class__, logger.handlers):
    logger.addHandler(SentryHandler())
    logger = logging.getLogger('sentry.errors')
    logger.propagate = False
    logger.addHandler(logging.StreamHandler())
    SENTRY_REMOTE_URL = 'http://sentry.ccnmtl.columbia.edu/sentry/store/'

try:
    from local_settings import *
except ImportError:
    pass
