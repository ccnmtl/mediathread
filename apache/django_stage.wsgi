import os, sys, site

# enable the virtualenv
site.addsitedir('/usr/local/share/sandboxes/common/mediathread/mediathread/ve/lib/python2.5/site-packages')

# paths we might need to pick up the project's settings
sys.path.append('/usr/local/share/sandboxes/common/')
sys.path.append('/usr/local/share/sandboxes/common/mediathread/')
sys.path.append('/usr/local/share/sandboxes/common/mediathread/mediathread/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'mediathread.settings_stage'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
