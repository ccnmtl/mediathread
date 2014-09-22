./manage.py dumpdata --settings=mediathread.settings_test --exclude --indent=4 > mediathread/main/fixtures/sample_course.json
./manage.py dumpdata --settings=mediathread.settings_test --exclude contenttypes --exclude tagging --indent=4 > mediathread/main/fixtures/unittest_sample_course.json
