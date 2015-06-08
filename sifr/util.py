import datetime
from dateutil import parser
import six


def normalize_time(t):
    try:
        if isinstance(t, datetime.datetime):
            return t
        elif isinstance(t, datetime.date):
            return datetime.datetime(t.year, t.month, t.day)
        elif isinstance(t, (int, float)):
            return datetime.datetime.fromtimestamp(t)
        elif isinstance(t, six.string_types):
            return parser.parse(t)
        else:
            raise TypeError
    except:  # noqa
        raise TypeError(
            "time must be represented as either a timestamp (int,float), "
            "a datetime.(datetime/date) object, "
            "or an iso-8601 formatted string. Not %s" % t.__class__.__name__
        )
