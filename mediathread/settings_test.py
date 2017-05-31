# flake8: noqa
from settings_shared import *

DEBUG = False
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

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

BROWSER = 'Headless'
# BROWSER = 'Firefox'
# BROWSER = 'Chrome'

LETTUCE_SERVER_PORT = 8002

LETTUCE_APPS = (
    'mediathread.assetmgr',
    'mediathread.discussions',
    'mediathread.main',
    'mediathread.projects',
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
    'impersonate.middleware.ImpersonateMiddleware')

ALLOWED_HOSTS.append('127.0.0.1')
