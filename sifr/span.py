import calendar
import datetime
import time
from sifr.util import normalize_time

try:
    from functools import total_ordering
except ImportError:
    from sifr.backports.total_ordering import total_ordering


@total_ordering
class Span(object):
    def __init__(self, at, keys, expiry=None):
        if not expiry and not isinstance(self, Forever):
            next = SPAN_ORDER.index(self.__class__) + 1
            if next < len(SPAN_ORDER):
                self.expiry = time.mktime(
                    (
                        normalize_time(at) + datetime.timedelta(
                            seconds=SPAN_ORDER[next].duration
                        )
                    ).timetuple()
                )
            else:
                self.expiry = None
        else:
            self.expiry = expiry
        self.at = normalize_time(at)
        self._key = ":".join([str(k) for k in keys])

    @property
    def key(self):
        return "{key}:{time}".format(key=self._key,
                                     time=self.at.strftime(self.fmt))

    @property
    def namespace(self):
        return self._key

    @property
    def timestamp(self):
        return self.at.strftime(self.fmt)

    @property
    def next(self):
        n = self.__class__(self.range[1] + datetime.timedelta(seconds=1), [])
        n._key = self._key
        return n

    def __lt__(self, other):
        return self.at < other.at

    def __repr__(self):  # pragma: no cover
        return self.at.strftime(self.fmt)


class Minute(Span):
    fmt = "%Y-%m-%d_%H:%M"
    duration = 60

    @property
    def range(self):
        return (datetime.datetime(year=self.at.year,
                                  month=self.at.month,
                                  day=self.at.day,
                                  hour=self.at.hour,
                                  minute=self.at.minute),
                datetime.datetime(year=self.at.year,
                                  month=self.at.month,
                                  day=self.at.day,
                                  hour=self.at.hour,
                                  minute=self.at.minute,
                                  second=59))


class Hour(Span):
    fmt = "%Y-%m-%d_%H"
    duration = 60 * 60

    @property
    def range(self):
        return (datetime.datetime(year=self.at.year,
                                  month=self.at.month,
                                  day=self.at.day,
                                  hour=self.at.hour),
                datetime.datetime(year=self.at.year,
                                  month=self.at.month,
                                  day=self.at.day,
                                  hour=self.at.hour,
                                  minute=59,
                                  second=59))


class Day(Span):
    fmt = "%Y-%m-%d"
    duration = 60 * 60 * 24

    @property
    def range(self):
        return (datetime.datetime(year=self.at.year,
                                  month=self.at.month,
                                  day=self.at.day),
                datetime.datetime(year=self.at.year,
                                  month=self.at.month,
                                  day=self.at.day,
                                  hour=23,
                                  minute=59,
                                  second=59))


class Month(Span):
    fmt = "%Y-%m"
    duration = 60 * 60 * 24 * 30

    @property
    def range(self):
        return (datetime.datetime(year=self.at.year,
                                  month=self.at.month,
                                  day=1),
                datetime.datetime(
                    year=self.at.year,
                    month=self.at.month,
                    day=calendar.monthrange(self.at.year, self.at.month)[1],
                    hour=23,
                    minute=59,
                    second=59))


class Year(Span):
    fmt = "%Y"
    duration = 60 * 60 * 24 * 365

    @property
    def range(self):
        return (datetime.datetime(year=self.at.year,
                                  month=1,
                                  day=1),
                datetime.datetime(year=self.at.year,
                                  month=12,
                                  day=calendar.monthrange(self.at.year, 12)[1],
                                  hour=23,
                                  minute=59,
                                  second=59))


class Forever(Span):
    fmt = "I"
    duration = -1

ALL_SPANS = [Year, Month, Day, Hour, Minute]
SPAN_ORDER = [Minute, Hour, Day, Month, Year]


def get_time_spans(start, end, keys, buckets=ALL_SPANS):
    spans = []
    buckets = list(buckets)
    if buckets:
        cur_bucket = buckets[0](start, keys)
        while cur_bucket.range[1] <= end:
            if start <= cur_bucket.range[0] and cur_bucket.range[1] <= end:
                spans.append(cur_bucket)
            cur_bucket = cur_bucket.next
        buckets.pop(0)
        if spans:
            min_left = min(spans).range[0]
            max_right = max(spans).range[1]
            spans.extend(get_time_spans(start, min_left, keys, list(buckets)))
            spans.extend(get_time_spans(max_right, end, keys, list(buckets)))
        else:
            spans.extend(get_time_spans(start, end, keys, list(buckets)))
    return sorted(spans)
