from django.test import TestCase
from mediathread.sequence.tests.factories import (
    SequenceAssetFactory,
    SequenceMediaElementFactory,
    SequenceTextElementFactory,
)


class SequenceAssetTest(TestCase):
    def setUp(self):
        self.asset = SequenceAssetFactory()

    def test_is_valid_from_factory(self):
        self.asset.full_clean()


class SequenceMediaElementTest(TestCase):
    def setUp(self):
        self.item = SequenceMediaElementFactory()

    def test_is_valid_from_factory(self):
        self.item.full_clean()


class SequenceTextElementTest(TestCase):
    def setUp(self):
        self.item = SequenceTextElementFactory()

    def test_is_valid_from_factory(self):
        self.item.full_clean()
