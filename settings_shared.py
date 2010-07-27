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
MEDIA_ROOT = "/var/www/mediathread/uploads/"
MEDIA_URL = '/uploads/'
ADMIN_MEDIA_PREFIX = '/media/'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
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
    'someutils.AuthRequirementMiddleware',
    'djangohelpers.middleware.HttpDeleteMiddleware',
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

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.markup',
    'sorl.thumbnail',
    'django.contrib.admin',
    'tagging',
    'smartif',
    'modelversions',
    #mediathread local
    'structuredcollaboration',
    'courseaffils',
    'djangosherd',#strangely must precede assetmgr
    'assetmgr',
    'projects',
    'discussions',

    'django.contrib.comments',
    'threadedcomments',
    'djangohelpers',
    #mediathread local
    #'slider',
    'mediathread_main',
)

THUMBNAIL_SUBDIR = "thumbs"
EMAIL_SUBJECT_PREFIX = "[mediathread] "
EMAIL_HOST = 'localhost'
SERVER_EMAIL = "mediathread@example.com"
PUBLIC_CONTACT_EMAIL = "mediathread@example.com"

# TinyMCE settings

TINYMCE_JS_URL = '/site_media/js/tiny_mce/tiny_mce.js'
TINYMCE_JS_ROOT = 'media/js/tiny_mce'

# if you set this to True, you may have to 
# override TINYMCE_JS_ROOT with the full path on production
TINYMCE_COMPRESSOR = False 
TINYMCE_SPELLCHECKER = True

TINYMCE_DEFAULT_CONFIG = {'cols': 80, 
                          'rows': 30,
                          'plugins':'table,spellchecker,paste,searchreplace',
                          'theme' : 'simple',
                          }

DATE_FORMAT = DATETIME_FORMAT = "g:i a, m/d/y"
LOGOUT_REDIRECT_URL = LOGIN_REDIRECT_URL = '/'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True


# for AuthRequirementMiddleware. this should be a list of 
# url prefixes for paths that can be accessed by anonymous
# users. we need to allow anonymous access to the login
# page, and to static resources.

ANONYMOUS_PATHS = ('/accounts/',
                   '/site_media/',
                   '/admin/',
                   )

COURSEAFFILS_PATHS = ('/asset/',
                      '/annotations/',
                      '/save',
                      '/yourspace/',
                      '/project/',
                      '/explore/',
                      '/comments/',
                      '/discussion/',
                      re.compile(r'^/$'),
                      )

NON_ANONYMOUS_PATHS = COURSEAFFILS_PATHS

COURSEAFFILS_EXEMPT_PATHS = ANONYMOUS_PATHS
COURSEAFFIL_AUTO_MAP_GROUPS = ['demo']

COMMENTS_ALLOW_PROFANITIES = True
COMMENTS_APP = 'threadedcomments'

FORCE_LOWERCASE_TAGS = True

#if you set this to a string, then bookmarklet can import from flickr
DJANGOSHERD_FLICKR_APIKEY = None
FLOWPLAYER_SWF_LOCATION = "http://releases.flowplayer.org/swf/flowplayer-3.2.2.swf"

#from courseaffils.models import InstructorManaged
from courseaffils import policies
DEFAULT_COLLABORATION_POLICY = policies.InstructorManaged()

#if you add a 'deploy_specific' directory
#then you can put a settings.py file and templates/ overrides there
try:
    from mediathread.deploy_specific.settings import *
    if locals().has_key('EXTRA_INSTALLED_APPS'):
        INSTALLED_APPS = EXTRA_INSTALLED_APPS + INSTALLED_APPS

except ImportError:
    pass
