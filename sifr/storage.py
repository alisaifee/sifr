from abc import abstractmethod, ABCMeta
import threading
import time

import six

from sifr.hll import HLL

try:
    from collections import Counter
except ImportError:  # pragma: no cover
    from .backports.counter import Counter  # pragma: no cover


@six.add_metaclass(ABCMeta)
class Storage(object):
    @abstractmethod
    def incr(self, span, amount=1):
        raise NotImplemented

    @abstractmethod
    def incr_unique(self, span, identifier, amount=1):
        raise NotImplemented

    @abstractmethod
    def track(self, span, identifier):
        raise NotImplemented

    @abstractmethod
    def get(self, span):
        raise NotImplemented

    @abstractmethod
    def get_unique(self, span):
        raise NotImplemented

    @abstractmethod
    def enumerate(self, span):
        raise NotImplemented


class LockableEntry(threading._RLock):
    __slots__ = ["atime", "expiry"]

    def __init__(self, expiry):
        self.atime = time.time()
        self.expiry = self.atime + expiry
        super(LockableEntry, self).__init__()


class HLLCounter(Counter):
    def __init__(self):
        self.counter = {}

    def pop(self, key):
        self.counter.pop(key, None)

    def add(self, key, identifier):
        self.counter.setdefault(key, HLL())
        self.counter[key].add(identifier)

    def get(self, key):
        if not key in self.counter:
            return 0
        return self.counter[key].count()


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
        for key in list(self.expirations.keys()):
            self.__check_expiry(key)

    def __schedule_expiry(self):
        if not self.timer.is_alive():
            self.timer = threading.Timer(0.01, self.__expire_events)
            self.timer.start()

    def __check_expiry(self, key):
        if self.expirations.get(key, 0) <= time.time():
            self.counter.pop(key, None)
            self.unique_counter.pop(key)
            self.tracker.pop(key, None)
            self.expirations.pop(key, None)

    def enumerate(self, span):
        self.__check_expiry(span.key)
        if not span.key in self.tracker:
            return set()
        else:
            return self.tracker.get(span.key)

    def get(self, span):
        self.__check_expiry(span.key)
        return self.counter.get(span.key, 0)

    def get_unique(self, span):
        self.__check_expiry(span.key)
        return self.unique_counter.get(span.key)

    def track(self, span, identifier):
        self.expirations[span.key] = span.expiry
        self.tracker.setdefault(span.key, set())
        self.tracker[span.key].add(identifier)

    def incr(self, span, amount=1):
        self.get(span)
        self.__schedule_expiry()
        self.expirations[span.key] = span.expiry
        self.counter[span.key] += amount

    def incr_unique(self, span, identifier):
        self.get_unique(span)
        self.__schedule_expiry()
        self.expirations[span.key] = span.expiry
        self.unique_counter.add(span.key, identifier)


class RedisStorage(Storage):
    def __init__(self, redis):
        self.redis = redis

    def track(self, span, identifier):
        with self.redis.pipeline() as pipeline:
            pipeline.sadd(span.key, identifier)
            pipeline.expireat(span.key, int(span.expiry))
            pipeline.execute()

    def enumerate(self, span):
        return self.redis.smembers(span.key) or set()

    def get(self, span):
        value = self.redis.get(span.key)
        return int(value) if value is not None else 0

    def incr_unique(self, span, identifier, amount=1):
        with self.redis.pipeline() as pipeline:
            pipeline.pfadd(span.key, identifier)
            pipeline.expireat(span.key, int(span.expiry))
            pipeline.execute()

    def incr(self, span, amount=1):
        with self.redis.pipeline() as pipeline:
            pipeline.incr(span.key)
            pipeline.expireat(span.key, int(span.expiry))
            pipeline.execute()

    def get_unique(self, span):
        value = self.redis.pfcount(span.key)
        return int(value) if value is not None else 0
