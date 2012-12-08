import unittest
from projects.tests.test_api import ProjectResourceTest


def suite():
    suite = unittest.TestSuite()

    suite.addTest(
        unittest.TestLoader().loadTestsFromTestCase(ProjectResourceTest))

    return suite
