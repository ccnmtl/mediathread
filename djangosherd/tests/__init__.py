import unittest
from djangosherd.tests.test_model import SherdNoteTest
from djangosherd.tests.test_api import SherdNoteResourceTest


def suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(SherdNoteTest))

    suite.addTest(
        unittest.TestLoader().loadTestsFromTestCase(SherdNoteResourceTest))

    return suite
