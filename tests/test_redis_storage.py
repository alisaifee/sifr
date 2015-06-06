import unittest
import datetime
import hiro
import redis
from sifr.span import Minute, Day
from sifr.storage import MemoryStorage, RedisStorage


class RedisStorageTests(unittest.TestCase):
    def setUp(self):
        self.redis = redis.Redis()
        self.redis.flushall()

    def test_incr_simple_minute(self):
        span = Minute(datetime.datetime.now(), ["minute_span"])
        storage = RedisStorage(self.redis)
        storage.incr(span)
        storage.incr(span)
        self.assertEqual(storage.get(span), 2)

    def test_incr_unique_minute(self):
        red = redis.Redis()
        span = Minute(datetime.datetime.now(), ["minute_span"])
        storage = RedisStorage(red)
        storage.incr_unique(span, "1")
        storage.incr_unique(span, "1")
        storage.incr_unique(span, "2")
        self.assertEqual(storage.get_unique(span), 2)

    def test_tracker_minute(self):
        span = Minute(datetime.datetime.now(), ["minute_span"])
        storage = RedisStorage(self.redis)
        storage.track(span, "1")
        storage.track(span, "1")
        storage.track(span, "2")
        storage.track(span, "3")
        self.assertEqual(storage.enumerate(span), set(["1", "2", "3"]))
