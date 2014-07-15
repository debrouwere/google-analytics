import addressable
import utils
import query
from dateutil.parser import parse as parse_date


class Account(object):
    def __init__(self, raw, service):
        self.service = service
        self.raw = raw
        self.id = raw['id']
        self.name = raw['name']
        self.permissions = raw['permissions']['effective']

    @property
    @utils.memoize
    def webproperties(self):
        raw_properties = self.service.management().webproperties().list(
            accountId=self.id).execute()['items']
        _webproperties = [WebProperty(raw, self) for raw in raw_properties]
        return addressable.List(_webproperties, indices=['id', 'name'])

    @property
    @utils.memoize
    def columns(self, include_deprecated=False):
        is_unique = not include_deprecated

        if include_deprecated:
            is_included = lambda column: True
        else:
            is_included = lambda column: not column.is_deprecated

        items = self.service.metadata().columns().list(
            reportType='ga').execute()['items']
        _columns = [Column(item, self) for item in items]
        _filtered_columns = filter(is_included, _columns)
        return addressable.List(_filtered_columns, 
            indices=['id', 'slug', 'name'], unique=is_unique)

    @property
    @utils.memoize
    def metrics(self):
        return addressable.filter(lambda column: column.type == 'metric', self.columns)

    @property
    @utils.memoize
    def dimensions(self):
        return addressable.filter(lambda column: column.type == 'dimension', self.columns)

    @property
    @utils.memoize
    def segments(self):
        _segments = self.service.management().segments().list().execute()
        return addressable.List(_segments, indices=['id', 'name'])

    @property
    @utils.memoize
    def goals(self):
        raise NotImplementedError()

    @property
    def query(self, *vargs, **kwargs):
        """ A shortcut to the first profile of the first webproperty. """
        return self.webproperties[0].query(*vargs, **kwargs)

    def __repr__(self):
        return "<Account: {} ({})>".format(
            self.name, self.id)


class WebProperty(object):
    def __init__(self, raw, account):
        self.account = account
        self.raw = raw
        self.id = raw['id']
        self.name = raw['name']
        self.url = raw['websiteUrl']

    @property
    @utils.memoize
    def profiles(self):
        raw_profiles = self.account.service.management().profiles().list(
            accountId=self.account.id,
            webPropertyId=self.id).execute()['items']
        profiles = [Profile(raw, self) for raw in raw_profiles]
        return addressable.List(profiles, indices=['id', 'name'])        

    def query(self, *vargs, **kwargs):
        """ A shortcut to the first profile of this webproperty. """
        return self.profiles[0].query(*vargs, **kwargs)

    def __repr__(self):
        return "<WebProperty: {} ({})>".format(
            self.name, self.id)


class Profile(object):
    def __init__(self, raw, webproperty):
        self.raw = raw
        self.webproperty = webproperty
        self.id = raw['id']
        self.name = raw['name']

    def query(self, metrics=[], dimensions=[]):
        return query.CoreQuery(self, metrics=metrics, dimensions=dimensions)

    def live(self, metrics=[], dimensions=[]):
        return query.LiveQuery(self, metrics=metrics, dimensions=dimensions)

    def __repr__(self):
        return "<Profile: {} ({})>".format(
            self.name, self.id)


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

class Column(object):
    def __init__(self, raw, account):
        attributes = raw['attributes']
        self.raw = raw
        self.account = account
        self.id = raw['id']
        self.slug = raw['id'].split(':')[1]
        self.name = attributes['uiName']
        self.group = attributes['group']
        self.description = attributes['description']
        self.type = attributes['type'].lower()
        self.cast = DIMENSIONS.get(self.id) or TYPES.get(attributes['dataType']) or NOOP
        self.is_deprecated = attributes['status'] == 'DEPRECATED'
        self.is_allowed_in_segments = 'allowedInSegments' in attributes

    def __repr__(self):
        return "<{type}: {name} ({id})>".format(
            type=self.type.capitalize(), 
            name=self.name, 
            id=self.id
            )


class Segment(object):
    def __init__(self, raw, account):
        self.raw = raw
        self.id = raw['id']
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