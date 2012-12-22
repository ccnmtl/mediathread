import unittest
from projects.tests.test_api import ProjectResourceTest
from projects.tests.test_model import ProjectTest


def suite():
    suite = unittest.TestSuite()

    suite.addTest(
        unittest.TestLoader().loadTestsFromTestCase(ProjectTest))

    suite.addTest(
        unittest.TestLoader().loadTestsFromTestCase(ProjectResourceTest))

    return suite
