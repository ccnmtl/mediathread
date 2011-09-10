from mediathread.settings import *

DATABASE_ENGINE = 'postgresql_psycopg2'

DATABASE_NAME = 'mediathread_20110909'

TEMPLATE_DIRS = (
    "/usr/local/share/sandboxes/common/mediathread_archive/mediathread/templates",
)

MEDIA_ROOT = '/usr/local/share/sandboxes/common/mediathread_archive/uploads/'

DEBUG = False
TEMPLATE_DEBUG = DEBUG
