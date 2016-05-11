import unittest
from mediathread.main.templatetags.methtags import int_to_term


class IntToTermTests(unittest.TestCase):
    def test_int_to_term(self):
        self.assertIsNone(int_to_term('abc'))
        self.assertEqual(int_to_term(1), 'Spring')
        self.assertEqual(int_to_term(2), 'Summer')
        self.assertEqual(int_to_term(3), 'Fall')
        self.assertIsNone(int_to_term(0))
        self.assertIsNone(int_to_term(4))
        self.assertIsNone(int_to_term(6))
