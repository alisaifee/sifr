import unittest
import datetime
import hiro
from sifr.span import Minute, Year, Month, Day, Hour


class SpanTests(unittest.TestCase):
    def test_minute(self):
        with hiro.Timeline().freeze(datetime.datetime(2012, 12, 12)):
            now = datetime.datetime.now()
            span = Minute(now, ["single"])
            self.assertEqual(span.key, "single:2012-12-12_00:00")

    def test_hour(self):
        with hiro.Timeline().freeze(datetime.datetime(2012, 12, 12)):
            now = datetime.datetime.now()
            span = Hour(now, ["single"])
            self.assertEqual(span.key, "single:2012-12-12_00")

    def test_day(self):
        with hiro.Timeline().freeze(datetime.datetime(2012, 12, 12)):
            now = datetime.datetime.now()
            span = Day(now, ["single"])
            self.assertEqual(span.key, "single:2012-12-12")

    def test_month(self):
        with hiro.Timeline().freeze(datetime.datetime(2012, 12, 12)):
            now = datetime.datetime.now()
            span = Month(now, ["single"])
            self.assertEqual(span.key, "single:2012-12")

    def test_year(self):
        with hiro.Timeline().freeze(datetime.datetime(2012, 12, 12)):
            now = datetime.datetime.now()
            span = Year(now, ["single"])
            self.assertEqual(span.key, "single:2012")
