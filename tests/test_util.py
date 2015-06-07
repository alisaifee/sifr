import unittest
import datetime
import time
import hiro
from sifr.span import Minute, Year, Month, Day, Hour, get_time_spans
from sifr.util import normalize_time


class DatetimeTests(unittest.TestCase):
    def test_num(self):
        with hiro.Timeline().freeze(datetime.datetime(2012, 12, 12)):
            self.assertEqual(
                normalize_time(1.0).year,
                1970
            )
            self.assertEqual(
                normalize_time(1).year,
                1970
            )
            self.assertEqual(
                normalize_time(time.time()),
                datetime.datetime(2012, 12, 12, 0, 0, 0)
            )

    def test_str(self):
        self.assertEqual(
            normalize_time("1970-1-1 7:30:1"),
            datetime.datetime(1970, 1, 1, 7, 30, 1)
        )
        self.assertEqual(
            normalize_time("1970-1-1"),
            datetime.datetime(1970, 1, 1, 0, 0, 0)
        )
        self.assertEqual(
            normalize_time("2012-12-12"),
            datetime.datetime(2012, 12, 12, 0, 0, 0)
        )

    def test_datetime_obj(self):
        self.assertEqual(
            normalize_time(datetime.datetime(1970, 1, 1, 7, 30, 1)),
            datetime.datetime(1970, 1, 1, 7, 30, 1)
        )
        self.assertEqual(
            normalize_time(datetime.date(1970, 1, 1)),
            datetime.datetime(1970, 1, 1, 0, 0, 0)
        )

    def test_invalid_type(self):

        self.assertRaises(
            TypeError,
            normalize_time, "time!",
        )
        self.assertRaises(
            TypeError,
            normalize_time, [],
        )
