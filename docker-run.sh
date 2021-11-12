#!/bin/bash

cd /app/

if [[ "$SETTINGS" ]]; then
		export DJANGO_SETTINGS_MODULE="mediathread.$SETTINGS"
else
		export DJANGO_SETTINGS_MODULE="mediathread.settings_docker"
fi

if [ "$1" == "migrate" ]; then
		exec /ve/bin/python manage.py migrate --noinput
fi

if [ "$1" == "collectstatic" ]; then
		exec /ve/bin/python manage.py collectstatic --noinput
fi

if [ "$1" == "compress" ]; then
		exec /ve/bin/python manage.py compress
fi

if [ "$1" == "shell" ]; then
		exec /ve/bin/python manage.py shell
fi

if [ "$1" == "test" ]; then
		exec /ve/bin/python manage.py test
fi

if [ "$1" == "worker" ]; then
		exec /ve/bin/python manage.py celery worker
fi

if [ "$1" == "beat" ]; then
		exec /ve/bin/python manage.py celery beat
fi

# run arbitrary commands
if [ "$1" == "manage" ]; then
		shift
		exec /ve/bin/python manage.py "$@"
fi


if [ "$1" == "run" ]; then
		exec /ve/bin/gunicorn --env \
				 DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE \
				 mediathread.wsgi:application -b 0.0.0.0:8000 -w 3 \
				 --access-logfile=- --error-logfile=-
fi
