# flake8: noqa
from django.conf import settings
from mediathread.settings_shared import *
from ctlsettings.staging import common, init_sentry

locals().update(
    common(
        project=project,
        base=base,
        STATIC_ROOT=STATIC_ROOT,
        INSTALLED_APPS=INSTALLED_APPS,
        s3static=True,
        s3prefix="ccnmtl",
    ))

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 3600  # One Hour
    }
}

TEMPLATES[0]['DIRS'].insert(
    0,
    "/var/www/mediathread/mediathread/mediathread/deploy_specific/templates")


# if you add a 'deploy_specific' directory
# then you can put a settings.py file and templates/ overrides there
# otherwise, make sure you specify the correct database settings in your
# local_settings.py
try:
    from mediathread.deploy_specific.settings import *  # noqa
    if 'EXTRA_INSTALLED_APPS' in locals():
        INSTALLED_APPS = INSTALLED_APPS + EXTRA_INSTALLED_APPS  # noqa
except:  # nosec
    pass

# Override deploy_specific LTI config just for staging
LTI_TOOL_CONFIGURATION = {
    'title': 'Mediathread Staging',
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

# local_settings overrides everything
try:
    from mediathread.local_settings import *
except ImportError:
    pass

if hasattr(settings, 'SENTRY_DSN'):
    init_sentry(SENTRY_DSN)  # noqa F405
