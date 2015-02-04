# encoding: utf-8

import os
import copy
import datetime
import textwrap
import operator
from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta

from .functional import memoize, immutable, identity, soak, vectorize
from .server import single_serve


def simplify(value):
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    else:
        return value


def flatten(l):
    return reduce(operator.add, l)


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

    if isinstance(start, datetime.date):
        start = start.isoformat()
    if isinstance(stop, datetime.date):
        stop = stop.isoformat()

    return (start, stop)


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


# analogous to R's paste function
def paste(rows, connector='=', delimiter='&', pad=False):
    if isinstance(rows, dict):
        rows = rows.items()

    if pad:
        width = max([len(key) for key, value in rows])
        rows = [(key.ljust(width), value) for key, value in rows]

    return delimiter.join(
        [connector.join([key, unicode(value)]) for key, value in rows])


def format(string, **kwargs):
    return textwrap.dedent(string).format(**kwargs)


def translate(d, mapping):
    d = copy.copy(d)

    for src, dest in mapping.items():
        if src in d:
            d[dest] = d[src]
            del d[src]

    return d


def whitelist(d, allowed):
    return {k: v for k, v in d.items() if k in allowed}


def here(*segments):
    current = os.path.dirname(__file__)
    return os.path.realpath(os.path.join(current, '..', *segments))
