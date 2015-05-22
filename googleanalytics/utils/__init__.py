# encoding: utf-8

import os
import copy
import operator
import functools

from . import date
from .functional import memoize, immutable, identity, soak, vectorize
from .server import single_serve
from .string import format, affix, paste, cut


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
    from StringIO import StringIO
except ImportError:
    import builtins
    from io import StringIO


# return a path relative to the package root
def here(*segments):
    current = os.path.dirname(__file__)
    return os.path.realpath(os.path.join(current, '..', *segments))


# flatten nested lists
def flatten(l):
    return functools.reduce(operator.add, l)


# wrap scalars into a list
def wrap(obj):
    if isinstance(obj, list):
        return obj
    else:
        return [obj]


# substitute new dictionary keys
def translate(d, mapping):
    d = copy.copy(d)

    for src, dest in mapping.items():
        if src in d:
            d[dest] = d[src]
            del d[src]

    return d


# retain only whitelisted keys in a dictionary
def whitelist(d, allowed):
    return {k: v for k, v in d.items() if k in allowed}

# similar to whitelist, but ordered and returns only values, not keys
def pick(obj, allowed):
    if isinstance(obj, dict):
        get = lambda key: obj[key]
    else:
        get = lambda key: getattr(obj, key)

    values = []
    for key in allowed:
        values.append(get(key))

    return values


# test if an object is falsy or contains only falsy values
def isempty(obj):
    if isinstance(obj, list):
        return not len(list(filter(None, obj)))
    elif isinstance(obj, dict):
        return not len(obj)
    else:
        return not obj
