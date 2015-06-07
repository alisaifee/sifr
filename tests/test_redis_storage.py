import unittest
import datetime

import redis

from sifr.span import Minute, Hour
from sifr.storage import RedisStorage


class RedisStorageTests(unittest.TestCase):
    def setUp(self):
        self.redis = redis.Redis(decode_responses=True)
        self.redis.flushall()

    def test_incr_simple_minute(self):
        span = Minute(datetime.datetime.now(), ["minute_span"])
        storage = RedisStorage(self.redis)
        storage.incr(span)
        storage.incr(span)
        self.assertEqual(storage.count(span), 2)
        self.assertTrue(self.redis.ttl(span.key + ":c") > 3000)

    def test_incr_unique_minute(self):
        red = redis.Redis()
        span = Minute(datetime.datetime.now(), ["minute_span"])
        storage = RedisStorage(red)
        storage.incr_unique(span, "1")
        storage.incr_unique(span, "1")
        storage.incr_unique(span, "2")
        self.assertEqual(storage.cardinality(span), 2)
        self.assertTrue(self.redis.ttl(span.key + ":u") > 3000)

    def test_tracker_minute(self):
        span = Minute(datetime.datetime.now(), ["minute_span"])
        storage = RedisStorage(self.redis)
        storage.track(span, "1")
        storage.track(span, "1")
        storage.track(span, "2")
        storage.track(span, "3")
        self.assertEqual(storage.uniques(span), set(["1", "2", "3"]))
        self.assertTrue(self.redis.ttl(span.key + ":t") > 3000)

    def test_multi(self):
        storage = RedisStorage(self.redis)
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

        self.assertTrue(self.redis.ttl(spans[0].key + ":t") > 3000)
        self.assertTrue(self.redis.ttl(spans[1].key + ":t") > 3599*24)
