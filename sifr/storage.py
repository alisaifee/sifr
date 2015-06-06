from abc import abstractmethod, ABCMeta
import threading
import hyperloglog
import six
import time

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
    def track(self, span, identifier, limit):
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
        self.counter.setdefault(key, hyperloglog.HyperLogLog(0.01))
        self.counter[key].add(identifier)

    def get(self, key):
        if not key in self.counter:
            return 0
        return int(len(self.counter[key]))


class MemoryStorage(Storage):
    def __init__(self):
        self.lock = threading.RLock()
        self.unique_counter = HLLCounter()
        self.counter = Counter()
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
            self.expirations.pop(key, None)

    def enumerate(self, span):
        pass

    def get(self, span):
        self.__check_expiry(span.key)
        return self.counter.get(span.key, 0)

    def get_unique(self, span):
        self.__check_expiry(span.key)
        return self.unique_counter.get(span.key)

    def track(self, span, identifier, limit):
        pass

    def incr(self, span, amount=1):
        self.get(span)
        self.__schedule_expiry()
        self.expirations[span.key] = span.expiry
        self.counter[span.key] += amount
        return self.counter[span.key]

    def incr_unique(self, span, identifier):
        self.get_unique(span)
        self.__schedule_expiry()
        self.expirations[span.key] = span.expiry
        self.unique_counter.add(span.key, identifier)
        return self.unique_counter.get(span.key)
