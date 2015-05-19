# flake8: noqa
from settings_shared import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/Users/sdreher/workspace/mediathread/lettuce.db',
        'OPTIONS': {
            'timeout': 30,
        },
        'ATOMIC_REQUESTS': True
    }
}

# BROWSER = 'Firefox'
BROWSER = 'Headless'
# BROWSER = 'Chrome'

LETTUCE_APPS = (
    'mediathread.main',
    'mediathread.projects',
    'mediathread.assetmgr'
)

LETTUCE_DJANGO_APP = ['lettuce.django']
INSTALLED_APPS = INSTALLED_APPS + LETTUCE_DJANGO_APP

if 'migrate' not in sys.argv:
    MIDDLEWARE_CLASSES.append(
        'mediathread.local_settings.ExceptionLoggingMiddleware')
COMPRESS_ROOT = "/Users/sdreher/workspace/mediathread/media/"