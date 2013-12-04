# flake8: noqa
from mediathread.settings import *

TEMPLATE_DIRS = (
    "/var/www/mediathread/mediathread/mediathread/deploy_specific/templates",
    "/var/www/mediathread/mediathread/mediathread/templates",
)

MEDIA_ROOT = '/var/www/mediathread/uploads/'
# put any static media here to override app served static media
STATICMEDIA_MOUNTS = (
    ('/sitemedia', '/var/www/mediathread/mediathread/sitemedia'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mediathread',
        'HOST': '',
        'PORT': '',
        'USER': '',
        'PASSWORD': '',
    }
}

COMPRESS_ROOT = "/var/www/mediathread/mediathread/media/"
DEBUG = False
TEMPLATE_DEBUG = DEBUG
DEV_ENV = True

SENTRY_SITE = 'mediathread-dev'
SENTRY_SERVERS = ['http://sentry.ccnmtl.columbia.edu/sentry/store/']

if 'migrate' not in sys.argv:
    INSTALLED_APPS.append('raven.contrib.django')

    import logging
    from raven.contrib.django.handlers import SentryHandler
    logger = logging.getLogger()
    # ensure we havent already registered the handler
    if SentryHandler not in map(type, logger.handlers):
        logger.addHandler(SentryHandler())
        logger = logging.getLogger('sentry.errors')
        logger.propagate = False
        logger.addHandler(logging.StreamHandler())

try:
    from local_settings import *
except ImportError:
    pass
