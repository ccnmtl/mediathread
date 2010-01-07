from mondrian.settings import *

DATABASE_ENGINE = 'postgresql_psycopg2'

TEMPLATE_DIRS = (
    "/usr/local/share/sandboxes/common/mondrian/mondrian/templates",
)

MEDIA_ROOT = '/usr/local/share/sandboxes/common/mondrian/uploads/'

DEBUG = False
TEMPLATE_DEBUG = DEBUG
