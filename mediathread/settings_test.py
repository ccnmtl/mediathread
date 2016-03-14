# flake8: noqa
from settings_shared import *

DEBUG = False
TEMPLATE_DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': './lettuce.db',
        'OPTIONS': {
            'timeout': 30,
        },
        'ATOMIC_REQUESTS': True
    }
}

# BROWSER = 'Firefox'
BROWSER = 'Headless'
# BROWSER = 'Chrome'

LETTUCE_SERVER_PORT = 8002

LETTUCE_APPS = (
    'mediathread.main',
    'mediathread.projects',
    'mediathread.assetmgr',
    'mediathread.taxonomy'
)

LETTUCE_DJANGO_APP = ['lettuce.django']
INSTALLED_APPS = INSTALLED_APPS + LETTUCE_DJANGO_APP

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

MIDDLEWARE_CLASSES.remove(
    'django_statsd.middleware.GraphiteRequestTimingMiddleware')
MIDDLEWARE_CLASSES.remove(
    'django_statsd.middleware.GraphiteMiddleware')
MIDDLEWARE_CLASSES.remove(
    'debug_toolbar.middleware.DebugToolbarMiddleware')
MIDDLEWARE_CLASSES.remove(
    'impersonate.middleware.ImpersonateMiddleware')
