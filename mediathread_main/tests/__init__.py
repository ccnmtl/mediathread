import unittest
from mediathread_main.tests.test_api import CourseResourceTest


def suite():
    suite = unittest.TestSuite()

    suite.addTest(
        unittest.TestLoader().loadTestsFromTestCase(CourseResourceTest))

    return suite
