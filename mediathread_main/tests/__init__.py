import unittest
from mediathread_main.tests.test_api import CourseResourceTest
from mediathread_main.tests.test_homepage import HomepageTest


def suite():
    suite = unittest.TestSuite()

    suite.addTest(
        unittest.TestLoader().loadTestsFromTestCase(CourseResourceTest))
    suite.addTest(
        unittest.TestLoader().loadTestsFromTestCase(HomepageTest))

    return suite
