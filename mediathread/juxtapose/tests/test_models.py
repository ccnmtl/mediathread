from django.test import TestCase
from mediathread.juxtapose.tests.factories import (
    JuxtaposeAssetFactory,
    JuxtaposeMediaElementFactory,
    JuxtaposeTextElementFactory,
)


class JuxtaposeAssetTest(TestCase):
    def setUp(self):
        self.asset = JuxtaposeAssetFactory()

    def test_is_valid_from_factory(self):
        self.asset.full_clean()


class JuxtaposeMediaElementTest(TestCase):
    def setUp(self):
        self.item = JuxtaposeMediaElementFactory()

    def test_is_valid_from_factory(self):
        self.item.full_clean()


class JuxtaposeTextElementTest(TestCase):
    def setUp(self):
        self.item = JuxtaposeTextElementFactory()

    def test_is_valid_from_factory(self):
        self.item.full_clean()
