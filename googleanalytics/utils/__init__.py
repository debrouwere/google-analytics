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
def paste(rows, *delimiters):
    delimiter = delimiters[-1]
    delimiters = delimiters[:-1]

    if len(delimiters):
        return paste([paste(row, *delimiters) for row in rows], delimiter)
    else:
        return delimiter.join(map(unicode, rows))

# the inverse of `paste`
def cut(s, *delimiters):
    delimiter = delimiters[-1]
    delimiters = delimiters[:-1]

    if len(delimiters):
        return [cut(ss, *delimiters) for ss in cut(s, delimiter)]
    else:
        return s.split(delimiter)


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


def isempty(obj):
    if isinstance(obj, list):
        return not len(list(filter(None, obj)))
    elif isinstance(obj, dict):
        return not len(obj)
    else:
        return not obj

def here(*segments):
    current = os.path.dirname(__file__)
    return os.path.realpath(os.path.join(current, '..', *segments))
