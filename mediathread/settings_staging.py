# flake8: noqa
from settings_shared import *
from ccnmtlsettings.staging import common

locals().update(
    common(
        project=project,
        base=base,
        STATIC_ROOT=STATIC_ROOT,
        INSTALLED_APPS=INSTALLED_APPS,
        s3static=False,
    ))


TEMPLATE_DIRS.insert(
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
except:
    pass

# local_settings overrides everything
try:
    from local_settings import *
except ImportError:
    pass
