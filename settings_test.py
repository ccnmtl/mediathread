from settings_shared import *
DATABASE_ENGINE = 'sqlite3' 
DATABASE_NAME = 'lettuce.db'
LETTUCE_SERVER_PORT = 8001

# Running tests
# Required in path: sqlite3 and Firefox
# Run ./bootstrapy.py --full to ensure necessary lxml dependencies are built
# ./manage.py harvest --settings=settings_test --debug-mode --verbosity=2
# http://lettuce.it/reference/cli.html

# Test data is automatically bootstrapped before the entire test run. 
# Some basic data is available
# Sample Course
# test_instructor / test
# test_student_one / test
# test_student_two / test
#
# 3 assets - 
# 1. YouTube CCNMTL Mediathread video w/
#    2 annotations
# 2. Flickr CCNTML Photo of Medical Center
#    1 annotation
# 3. Flickr CCNMTl Photo of Frank and Maurice
#    1 annotation

