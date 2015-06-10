import unittest
import datetime

import redis
import riak

from sifr.span import Minute, Hour
from sifr.storage import RedisStorage, RiakStorage


class RedisStorageTests(unittest.TestCase):
    def setUp(self):
        self.riak = riak.RiakClient(pb_port=8087, protocol='pbc')
        storage = RiakStorage(self.riak)
        for bucket in [storage.unique_counters_bucket, storage.uniques_bucket, storage.counter_bucket]:
            for key in bucket.get_keys():
                bucket.delete(key)

    def test_incr_simple_minute(self):
        span = Minute(datetime.datetime.now(), ["minute_span"])
        storage = RiakStorage(self.riak)
        storage.incr(span)
        storage.incr(span)
        self.assertEqual(storage.count(span), 2)

    def test_incr_unique_minute(self):
        span = Minute(datetime.datetime.now(), ["minute_span"])
        storage = RiakStorage(self.riak)
        storage.incr_unique(span, "1")
        storage.incr_unique(span, "1")
        storage.incr_unique(span, "2")
        self.assertEqual(storage.cardinality(span), 2)

    def test_tracker_minute(self):
        span = Minute(datetime.datetime.now(), ["minute_span"])
        storage = RiakStorage(self.riak)
        storage.track(span, "1")
        storage.track(span, "1")
        storage.track(span, "2")
        storage.track(span, "3")
        self.assertEqual(storage.uniques(span), set(["1", "2", "3"]))

    def test_multi(self):
        storage = RiakStorage(self.riak)
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
