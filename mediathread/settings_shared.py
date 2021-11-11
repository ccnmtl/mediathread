# Django settings for mediathread project.

# if you add a 'deploy_specific' directory
# then you can put a settings.py file and templates/ overrides there
# (see bottom)

import os.path
import re
import sys

from ccnmtlsettings.shared import common
from mediathread.assetmgr.sligen import sligen_streaming_processor


project = 'mediathread'
base = os.path.dirname(__file__)

locals().update(common(project=project, base=base))

PROJECT_APPS = [
    'mediathread.main',
    'mediathread.djangosherd',
    'mediathread.assetmgr',
    'mediathread.projects',
    'mediathread.reports',
    'mediathread.discussions',
    'mediathread.taxonomy',
    'structuredcollaboration',
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'mediathread',
        'TIMEOUT': 3600  # One Hour
    }
}

TEMPLATES[0]['OPTIONS']['context_processors'].append(  # noqa
    'mediathread.main.views.django_settings')

# Prepend the CookiesSameSite middleware to the beginning of
# MIDDLEWARE. It needs to be first to work correctly.
MIDDLEWARE = ['django_cookies_samesite.middleware.CookiesSameSite'] + \
    MIDDLEWARE  # noqa

MIDDLEWARE += [  # noqa
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'mediathread.main.middleware.MethCourseManagerMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
]


TEMPLATES[0]['DIRS'].insert(0, os.path.join(base, "deploy_specific/templates"))  # noqa


INSTALLED_APPS += [  # noqa
    'courseaffils',
    'tagging',
    'structuredcollaboration',
    'mediathread.assetmgr',
    'mediathread.djangosherd',
    'mediathread.projects',
    'mediathread.discussions',
    'mediathread.sequence',
    'threadedcomments',
    'django_comments',
    'djangohelpers',
    'mediathread.reports',
    'mediathread.main',
    'mediathread.taxonomy',
    'registration',
    'corsheaders',
    'reversion',
    'lti_auth',
    'bootstrap3',
    'bootstrap4',
    'django_extensions',
    'rest_framework',
    'django_celery_results',
    's3sign',
]

THUMBNAIL_SUBDIR = "thumbs"
SERVER_EMAIL = "mediathread@example.com"

DATE_FORMAT = DATETIME_FORMAT = "g:i a, m/d/y"
LOGOUT_REDIRECT_URL = LOGIN_REDIRECT_URL = '/'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//mediathread'
CELERY_WORKER_CONCURRENCY = 1

# for AuthRequirementMiddleware. this should be a list of
# url prefixes for paths that can be accessed by anonymous
# users. we need to allow anonymous access to the login
# page, and to static resources.

ANONYMOUS_PATHS = (
    '/media/',
    '/accounts/',
    '/admin/',
    '/help/',
    '/api/user/courses',
    '/sequence/api/',
    '/project/api/',
)

NON_ANONYMOUS_PATHS = (
    '/analysis/',
    '/annotations/',
    '/api/',
    '/archive/',
    '/asset/',
    '/assignment/',
    '/comments/',
    '/dashboard/',
    '/discussion/',
    '/explore/',
    '/impersonate/',
    '/project/',
    '/reports/',
    '/setting/',
    '/taxonomy/',
    '/upload/',
    re.compile(r'^/$'),
)

# save is an exception, for server2server api
COURSEAFFILS_PATHS = NON_ANONYMOUS_PATHS + ('/save', '/settings')

COURSEAFFILS_EXEMPT_PATHS = ANONYMOUS_PATHS
COURSEAFFIL_AUTO_MAP_GROUPS = ['demo']

COMMENTS_ALLOW_PROFANITIES = True
COMMENTS_APP = 'threadedcomments'
COMMENT_MAX_LENGTH = 20000

FORCE_LOWERCASE_TAGS = True

# specify FLICKR api key as a string
# https://www.flickr.com/services/api/misc.api_keys.html
DJANGOSHERD_FLICKR_APIKEY = 'undefined'

# specify YouTube browser api key as a string
# obtain a browser api key here:
# https://developers.google.com/youtube/registering_an_application#Create_API_Keys
YOUTUBE_BROWSER_APIKEY = 'undefined'

BOOKMARKLET_VERSION = '2'

# Mediathread instantiates a Flowplayer .swf to play many video flavors.
# Update this variable with your site's Flowplayer installation
# See README.markdown for more information
# expected: http://<server>/<directory>/flowplayer-3.2.18.swf
FLOWPLAYER_SWF_LOCATION = None
FLOWPLAYER_HTML5_LOCATION = None
# Specify your own plugin versions here. The player looks in the same
# http://<server>/<directory>/ specified above.
FLOWPLAYER_AUDIO_PLUGIN = 'flowplayer.audio-3.2.11.swf'
FLOWPLAYER_PSEUDOSTREAMING_PLUGIN = 'flowplayer.pseudostreaming-3.2.13.swf'
FLOWPLAYER_RTMP_PLUGIN = 'flowplayer.rtmp-3.2.13.swf'

DEFAULT_COLLABORATION_POLICY = 'InstructorManaged'

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

ACCOUNT_ACTIVATION_DAYS = 7

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_METHODS = ('GET',)
CORS_ALLOW_CREDENTIALS = True

DCS_SESSION_COOKIE_SAMESITE = 'None'


def default_url_processor(url, label=None, request=None):
    return url


ASSET_URL_PROCESSOR = default_url_processor

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'lti_auth.auth.LTIBackend',
]

LTI_TOOL_CONFIGURATION = {
    'title': 'Mediathread',
    'description': 'View and filter your Mediathread selections. '
    'A new icon will show up in your course rich editor letting you '
    'search and filter your Mediathread selections and click to '
    'embed selections in your course material.',
    'launch_url': 'lti/',
    'embed_url': 'asset/embed/',
    'embed_icon_url': 'img/icons/icon-16.png',
    'embed_tool_id': 'mediathread',
    'landing_url': '{}://{}/course/lti/{}/'
}

LTI_EXTRA_PARAMETERS = ['custom_course_context']

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

if 'test' in sys.argv or \
   'jenkins' in sys.argv or \
   'integrationserver' in sys.argv:
    DEBUG = True
    TEMPLATES[0]['OPTIONS']['debug'] = DEBUG  # noqa
    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
    )
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    if 'integrationserver' in sys.argv:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'mediathread',
                'HOST': 'localhost',
                'PORT': 5432,
                'USER': 'postgres',
                'PASSWORD': 'postgres',
                'ATOMIC_REQUESTS': True,
            }
        }

    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

    from celery.contrib.testing.app import DEFAULT_TEST_CONFIG

    CELERY_BROKER_URL = DEFAULT_TEST_CONFIG.get('broker_url')
    CELERY_RESULT_BACKEND = DEFAULT_TEST_CONFIG.get('result_backend')
    CELERY_BROKER_HEARTBEAT = DEFAULT_TEST_CONFIG.get('broker_heartbeat')

BLOCKED_EMAIL_DOMAINS = []

# django-tagging
MAX_TAG_LENGTH = 255
SURELINK_URL = ''

ASSET_URL_PROCESSOR = sligen_streaming_processor

IMAGE_UPLOAD_AVAILABLE = False
