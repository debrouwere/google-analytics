# encoding: utf-8

import re
import functools
import __builtin__

import addressable
from addressable import map, filter
from dateutil.parser import parse as parse_date

from .utils import identity, vectorize


TODO = identity

# TODO: percent, time, currency
TYPES = {
    'STRING': unicode, 
    'INTEGER': int, 
    'FLOAT': float, 
    'PERCENT': TODO, 
    'TIME': TODO, 
    'CURRENCY': TODO, 
}

DIMENSIONS = {
    'ga:date': parse_date, 
}


def escape_chars(value, chars=',;'):
    for char in chars:
        value = value.replace(char, '\\' + char)
    return value

def escape(method):
    @functools.wraps(method)
    def escaped_method(self, *values):
        values = __builtin__.map(escape_chars, values)
        return method(self, *values)
    return escaped_method


class Column(object):
    def __init__(self, raw, account):
        attributes = raw['attributes']
        self.raw = raw
        self.account = account
        self.id = raw['id']
        self.report_type, self.slug = self.id.split(':')
        self.pyslug = re.sub(r'([A-Z])', r'_\1', self.slug).lower()
        self.name = attributes['uiName']
        self.group = attributes['group']
        self.description = attributes['description']
        self.type = attributes['type'].lower()
        # TODO: evaluate if we can improve casting
        self.cast = DIMENSIONS.get(self.id) or TYPES.get(attributes['dataType']) or identity
        self.is_deprecated = attributes.get('status', 'ACTIVE') == 'DEPRECATED'
        self.is_allowed_in_segments = 'allowedInSegments' in attributes

    @escape
    def eq(self, value):
        return "{id}=={value}".format(id=self.id, value=value)

    @escape
    def neq(self, value):
        return "{id}!={value}".format(id=self.id, value=value)

    @escape
    def lt(self, value):
        return "{id}<{value}".format(id=self.id, value=value)

    @escape
    def lte(self, value):
        return "{id}<={value}".format(id=self.id, value=value)

    @escape
    def gt(self, value):
        return "{id}>{value}".format(id=self.id, value=value)

    @escape
    def gte(self, value):
        return "{id}>={value}".format(id=self.id, value=value)

    @escape
    def between(self, a, b):
        return "{id}<>{a}_{b}".format(id=self.id, a=a, b=b)

    @escape
    def any(self, *values):
        return "{id}[]{values}".format(id=self.id, values="|".join(values))

    @escape
    def contains(self, value):
        return "{id}=@{value}".format(id=self.id, value=value)

    @escape
    def ncontains(self, value):
        return "{id}!@{value}".format(id=self.id, value=value)

    @escape
    def re(self, value):
        return "{id}=~{value}".format(id=self.id, value=value)

    @escape
    def nre(self, value):
        return "{id}!~{value}".format(id=self.id, value=value)

    # useful when sorting a query
    def __neg__(self):
        return '-' + self.id

    def __repr__(self):
        report_types = {
            'ga': 'Core', 
            'rt': 'Realtime', 
            None: 'Unbound', 
        }
        return "<googleanalytics.columns.{query_type} object: {column_type}, {name} ({id})>".format(
            query_type=report_types[self.report_type],
            column_type=self.type.capitalize(), 
            name=self.name, 
            id=self.id
        )


# see https://developers.google.com/analytics/devguides/reporting/core/v3/segments#reference
class Segment(Column):
    # CHECK: do we need to call super here?
    def __init__(self, raw, account):
        self.raw = raw
        self.id = raw['segmentId']
        self.report_type, self.slug = self.id.split('::')        
        self.name = raw['name']
        self.kind = raw['kind'].lower()
        self.definition = raw['definition']

    def __repr__(self):
        return "<googleanalytics.columns.Segment object: {name} ({id})>".format(**self.__dict__)



class Filter(object):
    pass


class Goal(object):
    pass

    """
     goals = service.management().goals().list(
            accountId=firstAccountId,
            webPropertyId=firstWebpropertyId,
            profileId=firstProfileId).execute()
    """


class ColumnList(addressable.List):
    COLUMN_TYPE = Column

    def __init__(self, columns, **options):
        options['items'] = columns
        options['name'] = self.COLUMN_TYPE.__class__.__name__
        options['indices'] = ('id', 'name', 'slug')
        options['insensitive'] = True
        super(ColumnList, self).__init__(**options)

    def normalize(self, value):
        if isinstance(value, self.COLUMN_TYPE):
            return value
        else:
            return self[value]

    @vectorize
    def serialize(self, value, greedy=True):
        """
        Greedy serialization requires the value to either be a column 
        or convertible to a column, whereas non-greedy serialization 
        will pass through any string as-is and will only serialize 
        Column objects.

        Non-greedy serialization is useful when preparing queries with 
        custom filters or segments.
        """

        if greedy and not isinstance(value, Column):
            value = self.normalize(value)

        if isinstance(value, Column):
            return value.id
        else:
            return value


class SegmentList(ColumnList):
    COLUMN_TYPE = Segment


def is_deprecated(column):
    return column.is_deprecated

def is_supported(column):
    return not column.is_deprecated

def is_metric(column):
    return column.type == 'metric'

def is_dimension(column):
    return column.type == 'dimension'

def is_core(column):
    return column.report_type == 'ga'

def is_live(column):
    return column.report_type == 'rt'
