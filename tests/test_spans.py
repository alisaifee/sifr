import unittest
import datetime
import time
import hiro
from sifr.span import Minute, Year, Month, Day, Hour, get_time_spans


class SpanTests(unittest.TestCase):
    def test_minute(self):
        with hiro.Timeline().freeze(datetime.datetime(2012, 12, 12)):
            now = datetime.datetime.now()
            span = Minute(now, ["single"])
            self.assertEqual(span.key, "single:2012-12-12_00:00")
            self.assertEqual(span.expiry, time.time() + 60*60)

    def test_hour(self):
        with hiro.Timeline().freeze(datetime.datetime(2012, 12, 12)):
            now = datetime.datetime.now()
            span = Hour(now, ["single"])
            self.assertEqual(span.key, "single:2012-12-12_00")
            self.assertEqual(span.expiry, time.time() + 60*60*24)

    def test_day(self):
        with hiro.Timeline().freeze(datetime.datetime(2012, 12, 12)):
            now = datetime.datetime.now()
            span = Day(now, ["single"])
            self.assertEqual(span.key, "single:2012-12-12")
            self.assertEqual(span.expiry, time.time() + 60*60*24*30)

    def test_month(self):
        with hiro.Timeline().freeze(datetime.datetime(2012, 12, 12)):
            now = datetime.datetime.now()
            span = Month(now, ["single"])
            self.assertEqual(span.key, "single:2012-12")
            self.assertEqual(span.expiry, time.time() + 60*60*24*365)

    def test_year(self):
        with hiro.Timeline().freeze(datetime.datetime(2012, 12, 12)):
            now = datetime.datetime.now()
            span = Year(now, ["single"])
            self.assertEqual(span.key, "single:2012")
            self.assertEqual(span.expiry, None)

    def test_query_keys_default_buckets(self):
            self.assertEqual(
                [k.key for k in get_time_spans(
                    start=datetime.datetime(2012,12,29),
                    end=datetime.datetime(2013,2,1),
                    keys=["single"]
                )],
                ["single:2012-12-29",
                 "single:2012-12-30",
                 "single:2012-12-31",
                 "single:2013-01",
                 ]
            )

    def test_query_keys_single_bucket(self):
        with hiro.Timeline().freeze(datetime.datetime(2012, 12, 29)):
            self.assertTrue(
                len(get_time_spans(
                    start=datetime.datetime.now(),
                    end=datetime.datetime.now() + datetime.timedelta(days=34),
                    keys=["single"],
                    buckets=[Day]
                )) == 34
            )
