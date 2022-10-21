# flake8: noqa
from mediathread.settings_shared import *

# if you add a 'deploy_specific' directory
# then you can put a settings.py file and templates/ overrides there
# otherwise, make sure you specify the correct database settings in your
# local_settings.py
try:
    from mediathread.deploy_specific.settings import *  # noqa
    if 'EXTRA_INSTALLED_APPS' in locals():
        INSTALLED_APPS = INSTALLED_APPS + EXTRA_INSTALLED_APPS  # noqa
except ImportError:
    pass

# local_settings overrides everything
try:
    from mediathread.local_settings import *
except ImportError:
    pass
