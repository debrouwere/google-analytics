import datetime
import re

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


# Python 2 and 3 compatibility
try:
    basestring = basestring
except NameError:
    basestring = str


def serialize(value):
    if isinstance(value, datetime.date):
        return value.isoformat()
    else:
        return value


def extract(obj):
    if isinstance(obj, datetime.date):
        if hasattr(obj, 'date'):
            return obj.date()
        else:
            return obj
    else:
        raise ValueError("Can only extract date for type: date, datetime. Received: {}".format(obj))


def parse_description(s):
    today = datetime.date.today()
    if s == 'today':
        return today
    elif s == 'yesterday':
        return today - relativedelta(days=1)
    else:
        match = re.match('(\d+)daysAgo', s)
        if match:
            return today - relativedelta(days=int(match.group(1)))
        else:
            raise ValueError("Can only parse descriptions of the format: today, yesterday, ndaysAgo")


def normalize(obj):
    if obj == None:
        return None
    elif isinstance(obj, datetime.date):
        return extract(obj)
    elif isinstance(obj, basestring):
        try:
            return extract(parse(obj))
        except ValueError:
            try:
                return extract(parse_description(obj))
            except ValueError:
                raise ValueError("Cannot parse date or description: " + obj)
    else:
        raise ValueError("Can only normalize dates of type: date, datetime, basestring.")


def range(start=None, stop=None, months=0, days=0):
    yesterday = datetime.date.today() - relativedelta(days=1)
    start = normalize(start) or yesterday
    stop = normalize(stop)
    is_past = days < 0 or months < 0

    if days or months:
        if start and stop:
            raise Exception(
                "A daterange cannot be defined using stop alongside months or days.")
        else:
            if is_past:
                days = days + 1
            else:
                days = days - 1

            delta = relativedelta(days=days, months=months)

            stop = start + delta

    stop = stop or start
    return map(serialize, sorted((start, stop)))


def is_relative(datestring):
    return not '-' in datestring
