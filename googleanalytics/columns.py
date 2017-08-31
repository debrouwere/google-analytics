# encoding: utf-8

import functools
import re

import addressable
from addressable import filter, map

from snakify import snakify

from . import utils

TYPES = {
    'STRING': utils.unicode,
    'INTEGER': int,
    'FLOAT': float,
    'PERCENT': float,
    'TIME': float,
    'CURRENCY': float,
}

DIMENSIONS = {
    'ga:date': lambda date: utils.date.parse(date).date(),
    'ga:dateHour': lambda date: utils.date.parse('{} {}'.format(date[:8], date[8:])),
}

def escape_chars(value, chars=',;'):
    if value is True:
        return 'Yes'
    elif value is False:
        return 'No'

    value = utils.unicode(value)
    for char in chars:
        value = value.replace(char, '\\' + char)

    return value

def escape(method):
    @functools.wraps(method)
    def escaped_method(self, *values):
        values = utils.builtins.map(escape_chars, values)
        return method(self, *values)
    return escaped_method


class Column(object):
    selectors = (
        'eq',
        'neq',
        'lt',
        'lte',
        'gt',
        'gte',
        'between',
        'any',
        'contains',
        'ncontains',
        're',
        'nre',
        )

    @classmethod
    def from_metadata(cls, metadata):
        attributes = metadata['attributes']
        data_format = DIMENSIONS.get(metadata['id']) or TYPES.get(attributes['dataType']) or utils.identity
        is_deprecated = attributes.get('status', 'ACTIVE') == 'DEPRECATED'
        is_allowed_in_segments = 'allowedInSegments' in attributes
        column = Column(metadata['id'],
            column_type=attributes['type'].lower(),
            format=data_format,
            attributes=attributes,
            deprecated=is_deprecated,
            allowed_in_segments=is_allowed_in_segments,
            )
        return column.expand()

    def __init__(self, column_id, column_type, format=utils.unicode, attributes={},
            deprecated=False, allowed_in_segments=True):
        self.account = None
        self.id = column_id
        self.report_type, self.slug = self.id.split(':')
        index = re.search(r'\d{1,2}', self.slug)
        if index:
            self.index = int(index.group(0))
        else:
            self.index = None
        self.python_slug = snakify(self.slug)
        self.attributes = attributes
        self.name = attributes.get('uiName', column_id).replace('XX', str(self.index))
        self.group = attributes.get('group')
        self.description = attributes.get('description')
        self.type = column_type
        # TODO: evaluate if we can improve casting
        self.cast = format
        self.is_deprecated = deprecated
        self.is_allowed_in_segments = allowed_in_segments

    def link(self, account):
        self.account = account

    def expand(self):
        columns = []
        if 'XX' in self.id:
            min_index = int(self.attributes.get('minTemplateIndex', '1'))
            max_index = int(self.attributes.get('maxTemplateIndex', '20'))
            for i in range(min_index, max_index + 1):
                column = Column(self.id.replace('XX', str(i)),
                    column_type=self.type,
                    format=self.cast,
                    attributes=self.attributes,
                    deprecated=self.is_deprecated,
                    allowed_in_segments=self.is_allowed_in_segments,
                    )
                columns.append(column)
        else:
            columns = [self]

        return columns

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
        self.python_slug = snakify(self.slug)
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
        options['indices'] = ('name', 'id', 'slug', 'python_slug')
        options['insensitive'] = True
        super(ColumnList, self).__init__(**options)

    @utils.vectorize
    def normalize(self, value):
        if isinstance(value, self.COLUMN_TYPE):
            return value
        else:
            return self[value]

    @utils.vectorize
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
