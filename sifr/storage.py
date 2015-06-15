from abc import abstractmethod, ABCMeta
import threading
import time

import six

from sifr.hll import HLLCounter

try:
    from collections import Counter
except ImportError:  # pragma: no cover
    from .backports.counter import Counter  # pragma: no cover


@six.add_metaclass(ABCMeta)
class Storage(object):
    @abstractmethod
    def incr(self, span, amount=1):
        raise NotImplementedError

    @abstractmethod
    def incr_multi(self, spans, amount=1):
        raise NotImplementedError

    @abstractmethod
    def incr_unique(self, span, identifier):
        raise NotImplementedError

    @abstractmethod
    def incr_unique_multi(self, spans, identifier):
        raise NotImplementedError

    @abstractmethod
    def track(self, span, identifier):
        raise NotImplementedError

    @abstractmethod
    def track_multi(self, spans, identifier):
        raise NotImplementedError

    @abstractmethod
    def count(self, span):
        raise NotImplementedError

    @abstractmethod
    def cardinality(self, span):
        raise NotImplementedError

    @abstractmethod
    def uniques(self, span):
        raise NotImplementedError


class MemoryStorage(Storage):
    def __init__(self):
        self.lock = threading.RLock()
        self.unique_counter = HLLCounter()
        self.counter = Counter()
        self.tracker = {}
        self.expirations = {}
        self.timer = threading.Timer(0.01, self.__expire_events)
        self.timer.start()
        super(MemoryStorage, self).__init__()

    def __expire_events(self):
        with self.lock:
            for key in list(self.expirations.keys()):
                self.__check_expiry(key)

    def __schedule_expiry(self):
        if not self.timer.is_alive():
            self.timer = threading.Timer(0.01, self.__expire_events)
            self.timer.start()

    def __check_expiry(self, key):
        with self.lock:
            if (
                key in self.expirations
                and self.expirations[key] <= time.time()
            ):
                self.counter.pop(key, None)
                self.unique_counter.pop(key)
                self.tracker.pop(key, None)
                self.expirations.pop(key, None)

    def uniques(self, span):
        self.__check_expiry(span.key)
        if span.key not in self.tracker:
            return set()
        else:
            return self.tracker.get(span.key)

    def count(self, span):
        self.__check_expiry(span.key)
        return self.counter.get(span.key, 0)

    def cardinality(self, span):
        self.__check_expiry(span.key)
        return self.unique_counter.get(span.key)

    def track(self, span, identifier):
        if span.expiry is not None:
            self.expirations[span.key] = span.expiry
        self.tracker.setdefault(span.key, set())
        self.tracker[span.key].add(identifier)

    def track_multi(self, spans, identifier):
        for span in spans:
            self.track(span, identifier)

    def incr(self, span, amount=1):
        with self.lock:
            self.count(span)
            self.__schedule_expiry()
            if span.expiry is not None:
                self.expirations[span.key] = span.expiry
            self.counter[span.key] += amount

    def incr_multi(self, spans, amount=1):
        for span in spans:
            self.incr(span)

    def incr_unique(self, span, identifier):
        self.cardinality(span)
        self.__schedule_expiry()
        if span.expiry is not None:
            self.expirations[span.key] = span.expiry
        self.unique_counter.add(span.key, identifier)

    def incr_unique_multi(self, spans, identifier):
        for span in spans:
            self.incr_unique(span, identifier)


class RedisStorage(Storage):
    def __init__(self, redis):
        self.redis = redis

    def track(self, span, identifier):
        with self.redis.pipeline(transaction=False) as pipeline:
            pipeline.sadd(span.key + ":t", identifier)
            pipeline.expire(span.key + ":t",
                            int(span.expiry) - int(time.time()))
            pipeline.execute()

    def track_multi(self, spans, identifier):
        with self.redis.pipeline(transaction=False) as pipeline:
            for span in spans:
                pipeline.sadd(span.key + ":t", identifier)
                if span.expiry is not None:
                    pipeline.expire(
                        span.key + ":t",
                        int(span.expiry) - int(time.time())
                    )
            pipeline.execute()

    def uniques(self, span):
        return self.redis.smembers(span.key + ":t") or set()

    def count(self, span):
        value = self.redis.get(span.key + ":c")
        return int(value) if value is not None else 0

    def incr_unique(self, span, identifier):
        with self.redis.pipeline(transaction=False) as pipeline:
            pipeline.pfadd(span.key + ":u", identifier)
            pipeline.expire(span.key + ":u",
                            int(span.expiry) - int(time.time()))
            pipeline.execute()

    def incr_unique_multi(self, spans, identifier):
        with self.redis.pipeline(transaction=False) as pipeline:
            for span in spans:
                pipeline.pfadd(span.key + ":u", identifier)
                if span.expiry is not None:
                    pipeline.expire(
                        span.key + ":u",
                        int(span.expiry) - int(time.time())
                    )
            pipeline.execute()

    def incr(self, span, amount=1):
        with self.redis.pipeline(transaction=False) as pipeline:
            pipeline.incr(span.key + ":c")
            if span.expiry is not None:
                pipeline.expire(
                    span.key + ":c",
                    int(span.expiry) - int(time.time())
                )
            pipeline.execute()

    def incr_multi(self, spans, amount=1):
        with self.redis.pipeline(transaction=False) as pipeline:
            for span in spans:
                pipeline.incr(span.key + ":c")
                if span.expiry is not None:
                    pipeline.expire(
                        span.key + ":c",
                        int(span.expiry) - int(time.time())
                    )
            pipeline.execute()

    def cardinality(self, span):
        value = self.redis.pfcount(span.key + ":u")
        return int(value) if value is not None else 0


class RiakStorage(Storage):
    def __init__(self, riak):
        self.riak = riak
        self.counter_bucket = self.riak.bucket_type(
            "maps"
        ).bucket("sifr_counter")
        self.unique_counters_bucket = self.riak.bucket_type(
            "maps"
        ).bucket("sifr_unique_counter")
        self.uniques_bucket = self.riak.bucket_type(
            "maps"
        ).bucket("sifr_uniques")

    def count(self, span):
        map = self.counter_bucket.get(span.namespace)
        counter = map.counters.get(span.timestamp)
        return counter.value

    def incr(self, span, amount=1):
        map = self.counter_bucket.new(span.namespace)
        counter = map.counters.get(span.timestamp)
        counter.increment()
        map.store()

    def get_maps(self, bucket, spans, create=False):
        maps = {}
        namespaces = set(span.namespace for span in spans)
        for namespace in namespaces:
            if create:
                maps[namespace] = bucket.new(namespace)
            else:
                maps[namespace] = bucket.get(namespace)
        return maps

    def track_multi(self, spans, identifier):
        maps = self.get_maps(self.uniques_bucket, spans, True)
        for span in spans:
            riak_set = maps[span.namespace].sets.get(span.timestamp)
            riak_set.add(str(identifier))
        for map in maps.values():
            map.store()

    def incr_unique_multi(self, spans, identifier):
        maps = self.get_maps(self.unique_counters_bucket, spans, True)
        for span in spans:
            counter = maps[span.namespace].sets.get(span.timestamp)
            counter.add(str(identifier))
        for map in maps.values():
            map.store()

    def track(self, span, identifier):
        map = self.uniques_bucket.new(span.namespace)
        riak_set = map.sets.get(span.timestamp)
        riak_set.add(str(identifier))
        map.store()

    def incr_unique(self, span, identifier):
        map = self.unique_counters_bucket.new(span.namespace)
        riak_set = map.sets.get(span.timestamp)
        riak_set.add(str(identifier))
        map.store()

    def incr_multi(self, spans, amount=1):
        maps = self.get_maps(self.counter_bucket, spans, True)
        for span in spans:
            counter = maps[span.namespace].counters.get(span.timestamp)
            counter.increment(amount)
        for map in maps.values():
            map.store()

    def cardinality(self, span):
        map = self.unique_counters_bucket.get(span.namespace)
        riak_set = map.sets.get(span.timestamp)
        return len(riak_set)

    def uniques(self, span):
        map = self.uniques_bucket.get(span.namespace)
        riak_set = map.sets.get(span.timestamp)
        return riak_set.value
