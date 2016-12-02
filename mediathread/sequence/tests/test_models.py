from django.test import TestCase
from mediathread.sequence.models import (
    SequenceMediaElement, SequenceTextElement
)
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

    def test_update_track_elements(self):
        self.asset.update_track_elements([], [])
        self.assertEqual(SequenceMediaElement.objects.count(), 0)
        self.assertEqual(SequenceTextElement.objects.count(), 0)

        media_track = []
        for i in range(3):
            e = SequenceMediaElementFactory(sequence_asset=self.asset)
            media_track.append({
                'start_time': i,
                'end_time': i + 0.5,
                'media': e.media,
            })

        text_track = []
        for i in range(4):
            e = SequenceTextElementFactory(sequence_asset=self.asset)
            text_track.append({
                'start_time': i,
                'end_time': i + 0.5,
                'text': 'text {}'.format(i),
            })

        self.asset.update_track_elements(media_track, text_track)
        self.assertEqual(SequenceMediaElement.objects.count(), 3)
        self.assertEqual(SequenceTextElement.objects.count(), 4)

        el0 = SequenceTextElement.objects.filter(text='text 0').first()
        self.assertEqual(el0.start_time, 0)
        self.assertEqual(el0.end_time, 0.5)
        self.assertEqual(el0.sequence_asset, self.asset)


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
