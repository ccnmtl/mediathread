# Django settings for mediathread project.

# if you add a 'deploy_specific' directory
# then you can put a settings.py file and templates/ overrides there
# (see bottom)

from courseaffils import policies
import os.path
import re
import sys

DEBUG = True
TEMPLATE_DEBUG = DEBUG
ADMINS = (
    ('admin', 'mediathread@example.com'),
)

MANAGERS = ADMINS

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

if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'HOST': '',
            'PORT': '',
            'USER': '',
            'PASSWORD': '',
        }
    }

CACHE_BACKEND = 'locmem:///'

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = False
MEDIA_ROOT = "uploads/"
MEDIA_URL = '/uploads/'
ADMIN_MEDIA_PREFIX = '/media/'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# ## be careful: if you add/remove something here
# ## do the same with settings_production.py
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'mediathread_main.views.django_settings',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'courseaffils.middleware.CourseManagerMiddleware',
    'mediathread_main.middleware.AuthRequirementMiddleware',
    'djangohelpers.middleware.HttpDeleteMiddleware'
)

ROOT_URLCONF = 'mediathread.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates"
    # or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # Put application templates before these fallback ones:
    "/var/www/mediathread/templates/",
    os.path.join(os.path.dirname(__file__), "templates"),
)

LETTUCE_APPS = (
    'mediathread_main',
    'projects'
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.flatpages',
    'django.contrib.markup',
    'sorl.thumbnail',
    'courseaffils',
    'django.contrib.admin',
    'tagging',
    'smartif',
    'modelversions',
    'structuredcollaboration',
    'djangosherd',  # strangely must precede assetmgr
    'assetmgr',
    'projects',
    'discussions',
    'django.contrib.comments',
    'threadedcomments',
    'djangohelpers',
    'reports',
    'mediathread_main',
    'sentry.client',
    'south',
    'lettuce.django'
)


THUMBNAIL_SUBDIR = "thumbs"
EMAIL_SUBJECT_PREFIX = "[mediathread] "
EMAIL_HOST = 'localhost'
SERVER_EMAIL = "mediathread@example.com"
PUBLIC_CONTACT_EMAIL = "mediathread@example.com"

# External url for issue reporting system or e-mail notification
CONTACT_US_DESTINATION = ""

DATE_FORMAT = DATETIME_FORMAT = "g:i a, m/d/y"
LOGOUT_REDIRECT_URL = LOGIN_REDIRECT_URL = '/'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True


# for AuthRequirementMiddleware. this should be a list of
# url prefixes for paths that can be accessed by anonymous
# users. we need to allow anonymous access to the login
# page, and to static resources.

ANONYMOUS_PATHS = ('/site_media/',
                   '/accounts/',
                   '/admin/',
                   '/api/',
                   '/help/'
                   )

NON_ANONYMOUS_PATHS = ('/asset/',
                       '/annotations/',
                       '/contact/',
                       '/yourspace/',
                       '/project/',
                       '/explore/',
                       '/comments/',
                       '/reports/',
                       '/discussion/',
                       '/notifications/',
                       '/archive/',
                       '/assignment/',
                       '/dashboard/',
                       '/_main/',
                       '/analysis/',
                       re.compile(r'^/$'),
                       )

# save is an exception, for server2server api
COURSEAFFILS_PATHS = NON_ANONYMOUS_PATHS + ('/save', '/settings')

COURSEAFFILS_EXEMPT_PATHS = ANONYMOUS_PATHS
COURSEAFFIL_AUTO_MAP_GROUPS = ['demo']

COMMENTS_ALLOW_PROFANITIES = True
COMMENTS_APP = 'threadedcomments'
COMMENT_MAX_LENGTH = None

FORCE_LOWERCASE_TAGS = True

# if you set this to a string, then bookmarklet can import from flickr
DJANGOSHERD_FLICKR_APIKEY = None
FLOWPLAYER_SWF_LOCATION = \
    "http://releases.flowplayer.org/swf/flowplayer-3.2.2.swf"

# from courseaffils.models import InstructorManaged
DEFAULT_COLLABORATION_POLICY = policies.InstructorManaged()


# this gets around Django 1.2's stupidity for commenting
# we're already checking that the request is from someone in the class
def no_reject(request, reason):
    request.csrf_processing_done = True
    return None

CSRF_FAILURE_VIEW = no_reject

# if you add a 'deploy_specific' directory
# then you can put a settings.py file and templates/ overrides there
try:
    from mediathread.deploy_specific.settings import *
    if 'EXTRA_INSTALLED_APPS' in locals():
        INSTALLED_APPS = EXTRA_INSTALLED_APPS + INSTALLED_APPS
    if 'EXTRA_MIDDLEWARE_CLASSES' in locals():
        MIDDLEWARE_CLASSES = EXTRA_MIDDLEWARE_CLASSES + MIDDLEWARE_CLASSES
except ImportError:
    pass
