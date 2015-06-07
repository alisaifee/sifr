import unittest
import datetime
import hiro
from sifr.span import Minute, Day, Hour
from sifr.storage import MemoryStorage


class MemoryStorageTests(unittest.TestCase):
    def test_incr_simple_minute(self):
        with hiro.Timeline().freeze() as timeline:
            span = Minute(datetime.datetime.now(), ["minute_span"])
            storage = MemoryStorage()
            storage.incr(span)
            self.assertEqual(storage.count(span), 1)
            storage.incr(span)
            self.assertEqual(storage.count(span), 2)
            timeline.forward((60 * 60) + 1)
            self.assertEqual(storage.count(span), 0)

    def test_incr_simple_day(self):
        with hiro.Timeline().freeze() as timeline:
            span = Day(datetime.datetime.now(), ["day_span"])
            storage = MemoryStorage()
            storage.incr(span)
            self.assertEqual(storage.count(span), 1)
            timeline.forward((60 * 60 * 24 * 30) + 1)
            self.assertEqual(storage.count(span), 0)

    def test_incr_unique_minute(self):
        with hiro.Timeline().freeze() as timeline:
            span = Minute(datetime.datetime.now(), ["minute_span"])
            storage = MemoryStorage()
            storage.incr_unique(span, "1")
            self.assertEqual(storage.cardinality(span), 1)
            storage.incr_unique(span, "1")
            self.assertEqual(storage.cardinality(span), 1)
            storage.incr_unique(span, "2")
            self.assertEqual(storage.cardinality(span), 2)
            timeline.forward((60 * 60) + 1)
            self.assertEqual(storage.cardinality(span), 0)

    def test_tracker_minute(self):
        with hiro.Timeline().freeze() as timeline:
            span = Minute(datetime.datetime.now(), ["minute_span"])
            storage = MemoryStorage()
            storage.track(span, "1")
            storage.track(span, "1")
            storage.track(span, "2")
            storage.track(span, "3")
            self.assertEqual(storage.uniques(span), set(["1", "2", "3"]))
            timeline.forward((60 * 60) + 1)
            self.assertEqual(storage.uniques(span), set())

    def test_multi(self):
        with hiro.Timeline().freeze() as timeline:
            storage = MemoryStorage()
            spans = [
                Minute(datetime.datetime.now(), ["minute_span"]),
                Hour(datetime.datetime.now(), ["minute_span"])
            ]
            storage.incr_multi(spans)
            storage.incr_unique_multi(spans, "1")
            storage.incr_unique_multi(spans, "2")
            storage.track_multi(spans, "1")
            storage.track_multi(spans, "2")

            self.assertEqual(storage.count(spans[0]), 1)
            self.assertEqual(storage.count(spans[1]), 1)
            self.assertEqual(storage.cardinality(spans[0]), 2)
            self.assertEqual(storage.cardinality(spans[1]), 2)
            self.assertEqual(storage.uniques(spans[0]), set(["1", "2"]))
            self.assertEqual(storage.uniques(spans[1]), set(["1", "2"]))

            timeline.forward((60*60) + 1)

            self.assertEqual(storage.count(spans[0]), 0)
            self.assertEqual(storage.count(spans[1]), 1)
            self.assertEqual(storage.cardinality(spans[0]), 0)
            self.assertEqual(storage.cardinality(spans[1]), 2)
            self.assertEqual(storage.uniques(spans[0]), set())
            self.assertEqual(storage.uniques(spans[1]), set(["1", "2"]))

            timeline.forward((60*60*23) + 1)

            self.assertEqual(storage.count(spans[1]), 0)
            self.assertEqual(storage.cardinality(spans[1]), 0)
            self.assertEqual(storage.uniques(spans[1]), set())
