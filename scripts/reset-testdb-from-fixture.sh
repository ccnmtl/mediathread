#!/bin/bash

rm lettuce.db
./manage.py syncdb --settings=mediathread.settings_test --noinput
./manage.py migrate --settings=mediathread.settings_test --noinput
echo 'delete from django_content_type;' | sqlite3 lettuce.db
./manage.py loaddata mediathread/main/fixtures/sample_course.json --settings=mediathread.settings_test