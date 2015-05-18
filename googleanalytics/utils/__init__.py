# encoding: utf-8

import os
import copy
import textwrap
import operator
import functools

from . import date
from .functional import memoize, immutable, identity, soak, vectorize
from .server import single_serve


# Python 2 and 3 compatibility
try:
    basestring = basestring
    unicode = unicode
    input = raw_input
except NameError:
    basestring = str
    unicode = str
    input = input

try:
    import __builtin__ as builtins
except ImportError:
    import builtins





def flatten(l):
    return functools.reduce(operator.add, l)


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
        [connector.join(map(unicode, row)) for row in rows])


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
