from mediathread_main.tests.test_api import CourseResourceTest, \
    UserResourceTest
from mediathread_main.tests.test_homepage import HomepageTest
import unittest


def suite():
    suite = unittest.TestSuite()

    suite.addTest(
        unittest.TestLoader().loadTestsFromTestCase(UserResourceTest))
    suite.addTest(
        unittest.TestLoader().loadTestsFromTestCase(CourseResourceTest))
    suite.addTest(
        unittest.TestLoader().loadTestsFromTestCase(HomepageTest))

    return suite
