# flake8: noqa
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

ALLOWED_HOSTS = ['.ccnmtl.columbia.edu', 'localhost']

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

if 'test' in sys.argv or 'jenkins' in sys.argv:
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

JENKINS_TASKS = (
    # 'django_jenkins.tasks.run_pylint',
    'django_jenkins.tasks.with_coverage',
    'django_jenkins.tasks.run_pep8',
    'django_jenkins.tasks.run_pyflakes',
)

PROJECT_APPS = ['mediathread.main',
                'mediathread.djangosherd',
                'mediathread.assetmgr',
                'mediathread.projects',
                'mediathread.reports',
                'mediathread.discussions']

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--with-coverage',
    ('--cover-package=mediathread.main,mediathread.djangosherd,'
     'mediathread.assetmgr,mediathread.projects'),
]

CACHE_BACKEND = 'locmem:///'

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = False
MEDIA_ROOT = "/var/www/mediathread/uploads/"
MEDIA_URL = "/uploads/"
STATIC_URL = "/media/"

# Override the secret key with your own. This is for development only
SECRET_KEY = ')ng#)ef_u@_^zvvu@dxm7ql-yb^_!a6%v3v^j3b(mp+)l+5%@h'

# appends a slash if nothing is found without a slash.
APPEND_SLASH = True

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'stagingcontext.staging_processor',
    'django.core.context_processors.static',
    'mediathread.main.views.django_settings',
    'djangowind.context.context_processor',
)

MIDDLEWARE_CLASSES = [
    'django_statsd.middleware.GraphiteRequestTimingMiddleware',
    'django_statsd.middleware.GraphiteMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'courseaffils.middleware.CourseManagerMiddleware',
    'mediathread.main.middleware.AuthRequirementMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'impersonate.middleware.ImpersonateMiddleware',
]

ROOT_URLCONF = 'mediathread.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates"
    # or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # Put application templates before these fallback ones:
    "/var/www/mediathread/templates/",
    os.path.join(os.path.dirname(__file__), "deploy_specific/templates"),
    os.path.join(os.path.dirname(__file__), "templates"),
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.flatpages',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'courseaffils',
    'django.contrib.sites',
    'django.contrib.admin',
    'tagging',
    'modelversions',
    'structuredcollaboration',
    'mediathread.assetmgr',
    'mediathread.djangosherd',
    'mediathread.projects',
    'mediathread.discussions',
    'django.contrib.comments',
    'threadedcomments',
    'djangohelpers',
    'mediathread.reports',
    'mediathread.main',
    'south',
    'django_nose',
    'compressor',
    'django_jenkins',
    'mediathread.taxonomy',
    'smoketest',
    'debug_toolbar',
    'django_markwhat',
    'impersonate'
]

INTERNAL_IPS = ('127.0.0.1', )

DEBUG_TOOLBAR_PATCH_SETTINGS = False

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]


STATIC_ROOT = os.path.join(os.path.dirname(__file__), "../media")
STATICFILES_DIRS = (
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

COMPRESS_URL = "/media/"
COMPRESS_ROOT = "media/"

THUMBNAIL_SUBDIR = "thumbs"
EMAIL_SUBJECT_PREFIX = "[mediathread] "
EMAIL_HOST = 'localhost'
SERVER_EMAIL = "mediathread@example.com"

DATE_FORMAT = DATETIME_FORMAT = "g:i a, m/d/y"
LOGOUT_REDIRECT_URL = LOGIN_REDIRECT_URL = '/'
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True


# for AuthRequirementMiddleware. this should be a list of
# url prefixes for paths that can be accessed by anonymous
# users. we need to allow anonymous access to the login
# page, and to static resources.

ANONYMOUS_PATHS = ('/media/',
                   '/accounts/',
                   '/admin/',
                   '/help/',
                   '/api/user/courses'
                   )

NON_ANONYMOUS_PATHS = ('/asset/',
                       '/annotations/',
                       '/project/',
                       '/explore/',
                       '/comments/',
                       '/reports/',
                       '/discussion/',
                       '/archive/',
                       '/assignment/',
                       '/dashboard/',
                       '/analysis/',
                       '/taxonomy/',
                       '/api/',
                       '/setting/',
                       '/upgrade/',
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

# Mediathread instantiates a Flowplayer .swf to play many video flavors.
# Update this variable with your site's Flowplayer installation
# See README.markdown for more information
# expected: http://<server>/<directory>/flowplayer-3.2.18.swf
FLOWPLAYER_SWF_LOCATION = None
# Specify your own plugin versions here. The player looks in the same
# http://<server>/<directory>/ specified above.
FLOWPLAYER_AUDIO_PLUGIN = 'flowplayer.audio-3.2.11.swf'
FLOWPLAYER_PSEUDOSTREAMING_PLUGIN = 'flowplayer.pseudostreaming-3.2.13.swf'
FLOWPLAYER_RTMP_PLUGIN = 'flowplayer.rtmp-3.2.13.swf'


DEFAULT_COLLABORATION_POLICY = policies.InstructorManaged()


# this gets around Django 1.2's stupidity for commenting
# we're already checking that the request is from someone in the class
def no_reject(request, reason):
    request.csrf_processing_done = True
    return None

CSRF_FAILURE_VIEW = no_reject

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# if you add a 'deploy_specific' directory
# then you can put a settings.py file and templates/ overrides there
# otherwise, make sure you specify the correct database settings in your
# local_settings.py
try:
    from mediathread.deploy_specific.settings import *
    if 'EXTRA_INSTALLED_APPS' in locals():
        INSTALLED_APPS = INSTALLED_APPS + EXTRA_INSTALLED_APPS
    if 'EXTRA_MIDDLEWARE_CLASSES' in locals():
        MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + EXTRA_MIDDLEWARE_CLASSES
except:
    pass
