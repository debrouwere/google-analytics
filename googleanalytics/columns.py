import re
import functools
from dateutil.parser import parse as parse_date

"""
service.metadata().columns().list(reportType='ga').execute()

            {u'attributes': {u'dataType': u'STRING',
                             u'description': u'Name of the product being queried.',
                             u'group': u'Related Products',
                             u'status': u'PUBLIC',
                             u'type': u'DIMENSION',
                             u'uiName': u'Queried Product Name'},
             u'id': u'ga:queryProductName',
             u'kind': u'analytics#column'},

"""

TODO = NOOP = lambda x: x

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
    @functools.wraps
    def escaped_method(self, *values):
        values = map(escape_chars, values)
        return method(self, values)
    return escaped_method


class Column(object):
    def __init__(self, raw, account):
        attributes = raw['attributes']
        self.raw = raw
        self.account = account
        self.id = raw['id']
        self.slug = raw['id'].split(':')[1]
        self.pyslug = re.sub(r'([A-Z])', r'_\1', self.slug).lower()
        self.name = attributes['uiName']
        self.group = attributes['group']
        self.description = attributes['description']
        self.type = attributes['type'].lower()
        self.cast = DIMENSIONS.get(self.id) or TYPES.get(attributes['dataType']) or NOOP
        self.is_deprecated = attributes['status'] == 'DEPRECATED'
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
        return "<{type}: {name} ({id})>".format(
            type=self.type.capitalize(), 
            name=self.name, 
            id=self.id
            )


# see https://developers.google.com/analytics/devguides/reporting/core/v3/segments#reference
class Segment(Column):
    def __init__(self, raw, account):
        self.raw = raw
        self.id = raw['segmentId']
        self.name = raw['name']
        self.kind = raw['kind'].lower()
        self.definition = raw['definition']

    def __repr__(self):
        return "<Segment: {name} ({id})>".format(**self.__dict__)



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