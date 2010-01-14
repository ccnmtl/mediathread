from mondrian.settings import *

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    #'django.core.context_processors.debug',
    'django.core.context_processors.request',
    )

DATABASE_ENGINE = 'postgresql_psycopg2'

TEMPLATE_DIRS = (
    "/var/www/mondrian/mondrian/templates",
)

MEDIA_ROOT = '/var/www/mondrian/uploads/'

DEBUG = False
TEMPLATE_DEBUG = DEBUG

WIND_SERVICE = "cnmtl_full_p"
