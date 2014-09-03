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

COMPRESS_ROOT = "/var/www/mediathread/mediathread/media/"
DEBUG = False
TEMPLATE_DEBUG = DEBUG
STAGING_ENV = True

STATSD_PREFIX = 'mediathread-staging'

if 'migrate' not in sys.argv:
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')

try:
    from local_settings import *
except ImportError:
    pass
