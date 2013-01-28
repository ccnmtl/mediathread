from settings_shared import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'lettuce.db',
        'OPTIONS': {
            'timeout': 30,
        }
    }
}

LETTUCE_SERVER_PORT = 8002
STATSD_HOST = '127.0.0.1'
BROWSER = 'Chrome'

# Full run
# time(./manage.py harvest --settings=settings_test \
# --debug-mode --verbosity=2 --traceback)

# Run a particular file + scenario
# ./manage.py harvest \
# mediathread_main/features/manage_selection_visibility.feature \
# -d --settings=settings_test -s 1
