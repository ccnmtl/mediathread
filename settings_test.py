from settings_shared import *
DATABASE_ENGINE = 'sqlite3' 
DATABASE_NAME = 'lettuce.db'

# Running tests
# Required in path: sqlite3 and Firefox
# Run ./bootstrapy.py --full to ensure necessary lxml dependencies are built
# ./manage.py harvest --settings=settings_test

# Test data is automatically bootstrapped before the entire test run. 
# Some basic data is available
# Sample Course
# test_instructor / test
# test_student_one / test
# test_student_two / test
