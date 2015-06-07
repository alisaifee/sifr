import datetime
from dateutil import parser
import six


def normalize_time(t):
    try:
        if isinstance(t, (int, float)):
            return datetime.datetime.fromtimestamp(t)
        elif isinstance(t, (datetime.datetime, datetime.date)):
            return t
        elif isinstance(t, six.string_types):
            return parser.parse(t)
        else:
            raise
    except:
        raise TypeError(
            "time must be represented as either a timestamp (int,float)"
            "a datetime.datetime, or datetime.date object"
            "or an iso-8601 formatted string"
        )
