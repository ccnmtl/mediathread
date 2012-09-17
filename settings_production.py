from mediathread.settings import *

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    #'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'mediathread_main.views.django_settings',
    )

DATABASE_ENGINE = 'postgresql_psycopg2'

TEMPLATE_DIRS = (
    "/var/www/mediathread/mediathread/templates",
)

MEDIA_ROOT = '/var/www/mediathread/uploads/'

DEBUG = False
TEMPLATE_DEBUG = DEBUG

WIND_SERVICE = "cnmtl_full_p"

try:
    from local_settings import *
except ImportError:
    pass

