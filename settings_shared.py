# Django settings for mediathread project.

#if you add a 'deploy_specific' directory
#then you can put a settings.py file and templates/ overrides there
#(see bottom)

import os.path
import re

DEBUG = True
TEMPLATE_DEBUG = DEBUG
ADMINS = (
    ('admin', 'mediathread@example.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2' # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'mediathread' # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

CACHE_BACKEND = 'locmem:///'

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = False
MEDIA_ROOT = "uploads/"
MEDIA_URL = '/uploads/'
ADMIN_MEDIA_PREFIX = '/media/'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

### be careful: if you add/remove something here
### do the same with settings_production.py
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'mediathread_main.views.django_settings',
    )

MIDDLEWARE_CLASSES = (
    'django_statsd.middleware.GraphiteRequestTimingMiddleware',
    'django_statsd.middleware.GraphiteMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'courseaffils.middleware.CourseManagerMiddleware',
    'mediathread_main.middleware.AuthRequirementMiddleware',
    'djangohelpers.middleware.HttpDeleteMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'mediathread.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # Put application templates before these fallback ones:
    "/var/www/mediathread/templates/",
    os.path.join(os.path.dirname(__file__),"templates"),
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
    'djangosherd',#strangely must precede assetmgr
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
    'lettuce.django',
    'django_statsd',
)

STATSD_CLIENT = 'statsd.client'
STATSD_PREFIX = 'mediathread'
STATSD_HOST = 'localhost'
STATSD_PORT = 8125
STATSD_PATCHES = ['django_statsd.patches.db', ]

THUMBNAIL_SUBDIR = "thumbs"
EMAIL_SUBJECT_PREFIX = "[mediathread] "
EMAIL_HOST = 'localhost'
SERVER_EMAIL = "mediathread@example.com"
PUBLIC_CONTACT_EMAIL = "mediathread@example.com"

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
                      
                      '/analysis/',
                      re.compile(r'^/$'),
                      )

#save is an exception, for server2server api
COURSEAFFILS_PATHS = NON_ANONYMOUS_PATHS + ('/save','/settings')

COURSEAFFILS_EXEMPT_PATHS = ANONYMOUS_PATHS
COURSEAFFIL_AUTO_MAP_GROUPS = ['demo']

COMMENTS_ALLOW_PROFANITIES = True
COMMENTS_APP = 'threadedcomments'
COMMENT_MAX_LENGTH = None

FORCE_LOWERCASE_TAGS = True

#if you set this to a string, then bookmarklet can import from flickr
DJANGOSHERD_FLICKR_APIKEY = None
FLOWPLAYER_SWF_LOCATION = "http://releases.flowplayer.org/swf/flowplayer-3.2.2.swf"

#from courseaffils.models import InstructorManaged
from courseaffils import policies
DEFAULT_COLLABORATION_POLICY = policies.InstructorManaged()

#this gets around Django 1.2's stupidity for commenting
#we're already checking that the request is from someone in the class
def no_reject(request, reason):
    request.csrf_processing_done = True
    return None

CSRF_FAILURE_VIEW = no_reject

#if you add a 'deploy_specific' directory
#then you can put a settings.py file and templates/ overrides there
try:
    from mediathread.deploy_specific.settings import *
    if locals().has_key('EXTRA_INSTALLED_APPS'):
        INSTALLED_APPS = EXTRA_INSTALLED_APPS + INSTALLED_APPS

except ImportError:
    pass


