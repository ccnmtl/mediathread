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
DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEV_ENV = True

try:
    from local_settings import *
except ImportError:
    pass
