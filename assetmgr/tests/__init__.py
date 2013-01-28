import unittest
from assetmgr.tests.test_model import AssetTest
from assetmgr.tests.test_api import AssetResourceTest


def suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(AssetTest))

    suite.addTest(
        unittest.TestLoader().loadTestsFromTestCase(AssetResourceTest))

    return suite
