# flake8: noqa
from mediathread.settings import *

USE_X_FORWARDED_HOST=True

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
        'PORT': 6432,  # see /etc/pgbouncer/pgbouncer.ini
        'USER': '',
        'PASSWORD': '',
    }
}

COMPRESS_ROOT = "/var/www/mediathread/mediathread/media/"
DEBUG = False
TEMPLATE_DEBUG = DEBUG

SENTRY_SITE = 'mediathread'

if 'migrate' not in sys.argv:
    INSTALLED_APPS.append('sentry.client')

    import logging
    from sentry.client.handlers import SentryHandler
    logger = logging.getLogger()
    if SentryHandler not in map(lambda x: x.__class__, logger.handlers):
        logger.addHandler(SentryHandler())
        logger = logging.getLogger('sentry.errors')
        logger.propagate = False
        logger.addHandler(logging.StreamHandler())

try:
    from local_settings import *
except ImportError:
    pass
