from mediathread.settings import *

DATABASE_ENGINE = 'postgresql_psycopg2'

TEMPLATE_DIRS = (
    "/usr/local/share/sandboxes/common/mediathread/mediathread/templates",
)

MEDIA_ROOT = '/usr/local/share/sandboxes/common/mediathread/uploads/'

DEBUG = False
TEMPLATE_DEBUG = DEBUG
