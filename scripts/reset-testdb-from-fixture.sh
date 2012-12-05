#!/bin/bash

rm lettuce.db
echo 'create table test(idx integer primary key);' | sqlite3 lettuce.db
./manage.py syncdb --settings=settings_test --noinput
./manage.py migrate --settings=settings_test --noinput
echo 'delete from django_content_type;' | sqlite3 lettuce.db
./manage.py loaddata mediathread_main/fixtures/sample_course.json --settings=settings_test