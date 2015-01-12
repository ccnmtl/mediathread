from datetime import datetime, timedelta

from django.test.testcases import TestCase

from mediathread.discussions.utils import pretty_date


class DiscussionUtilsTest(TestCase):

    def test_pretty_date(self):
        timestamp = datetime.now()
        self.assertTrue('seconds ago' in pretty_date(timestamp))

        self.assertTrue('a minute ago' in
                        pretty_date(timestamp - timedelta(minutes=1)))

        self.assertTrue('minutes ago' in
                        pretty_date(timestamp - timedelta(minutes=2)))

        self.assertTrue('hour(s) ago' in
                        pretty_date(timestamp - timedelta(hours=3)))

        self.assertTrue('Yesterday' in
                        pretty_date(timestamp - timedelta(days=1)))

        timestamp = timestamp - timedelta(days=5)
        self.assertTrue('days ago' in pretty_date(timestamp))
