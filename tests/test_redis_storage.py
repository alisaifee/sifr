import unittest
import datetime

import redis

from sifr.span import Minute
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
        self.assertEqual(storage.get(span), 2)
        self.assertEqual(self.redis.ttl(span.key + ":c"), 60*60)

    def test_incr_unique_minute(self):
        red = redis.Redis()
        span = Minute(datetime.datetime.now(), ["minute_span"])
        storage = RedisStorage(red)
        storage.incr_unique(span, "1")
        storage.incr_unique(span, "1")
        storage.incr_unique(span, "2")
        self.assertEqual(storage.get_unique(span), 2)
        self.assertEqual(self.redis.ttl(span.key + ":u"), 60*60)

    def test_tracker_minute(self):
        span = Minute(datetime.datetime.now(), ["minute_span"])
        storage = RedisStorage(self.redis)
        storage.track(span, "1")
        storage.track(span, "1")
        storage.track(span, "2")
        storage.track(span, "3")
        self.assertEqual(storage.enumerate(span), set(["1", "2", "3"]))
        self.assertEqual(self.redis.ttl(span.key + ":t"), 60*60)