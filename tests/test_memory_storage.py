import unittest
import datetime
import hiro
from sifr.span import Minute, Day
from sifr.storage import MemoryStorage


class MemoryStorageTests(unittest.TestCase):
    def test_incr_simple_minute(self):
        with hiro.Timeline().freeze() as timeline:
            span = Minute(datetime.datetime.now(), ["minute_span"])
            storage = MemoryStorage()
            storage.incr(span)
            self.assertEqual(storage.get(span), 1)
            storage.incr(span)
            self.assertEqual(storage.get(span), 2)
            timeline.forward((60 * 60) + 1)
            self.assertEqual(storage.get(span), 0)

    def test_incr_simple_day(self):
        with hiro.Timeline().freeze() as timeline:
            span = Day(datetime.datetime.now(), ["day_span"])
            storage = MemoryStorage()
            storage.incr(span)
            self.assertEqual(storage.get(span), 1)
            timeline.forward((60 * 60 * 24 * 30) + 1)
            self.assertEqual(storage.get(span), 0)

    def test_incr_unique_minute(self):
        with hiro.Timeline().freeze() as timeline:
            span = Minute(datetime.datetime.now(), ["minute_span"])
            storage = MemoryStorage()
            storage.incr_unique(span, "1")
            self.assertEqual(storage.get_unique(span), 1)
            storage.incr_unique(span, "1")
            self.assertEqual(storage.get_unique(span), 1)
            storage.incr_unique(span, "2")
            self.assertEqual(storage.get_unique(span), 2)
            timeline.forward((60 * 60) + 1)
            self.assertEqual(storage.get_unique(span), 0)

    def test_tracker_minute(self):
        with hiro.Timeline().freeze() as timeline:
            span = Minute(datetime.datetime.now(), ["minute_span"])
            storage = MemoryStorage()
            storage.track(span, "1", 3)
            storage.track(span, "1", 3)
            storage.track(span, "2", 3)
            storage.track(span, "3", 3)
            self.assertEqual(storage.enumerate(span), set(["1", "2", "3"]))
            storage.track(span, "4", 3)
            self.assertEqual(storage.enumerate(span), set(["4", "2", "3"]))
            timeline.forward((60 * 60) + 1)
            self.assertEqual(storage.enumerate(span), set())
