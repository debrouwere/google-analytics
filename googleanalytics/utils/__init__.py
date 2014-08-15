import copy
import datetime
from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta

import flask
from functional import memoize, immutable, noop, soak
from server import single_serve

def date(obj):
    if obj is None:
        return None
    elif isinstance(obj, datetime.date):
        if hasattr(dt, 'date'):
            return obj.date()
        else:
            return obj
    elif isinstance(obj, basestring):
        return parse_date(obj).date()
    else:
        raise ValueError("Can only convert strings into dates, received {}".format(obj.__class__))


def date_or_description(obj):
    if isinstance(obj, basestring):
        if obj in ['today', 'yesterday']:
            return obj
        elif obj.endswith('daysAgo'):
            return obj
        else:
            return date(obj)


def daterange(start, stop=None, months=0, days=0):
    start = date_or_description(start)
    stop = date_or_description(stop)

    if days or months:
        if stop:
            raise Exception(
                "A daterange cannot be defined using stop alongside months or days.")

        stop = start + relativedelta(days=days-1, months=months)
    else:
        stop = stop or start

    return (start.isoformat(), stop.isoformat())


def wrap(obj):
    if isinstance(obj, list):
        return obj
    else:
        return [obj]


def affix(prefix, base, suffix, connector='_'):
    if prefix:
        prefix = prefix + connector
    else:
        prefix = ''

    if suffix:
        suffix = connector + suffix
    else:
        suffix = ''

    return prefix + base + suffix


def translate(d, mapping):
    d = copy.copy(d)

    for src, dest in mapping.items():
        if src in d:
            d[dest] = d[src]
            del d[src]

    return d
