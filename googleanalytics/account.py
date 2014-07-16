import addressable
import utils
from columns import Column, Segment
import query


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
        raw_segments = self.service.management().segments().list().execute()['items']
        return addressable.List([Segment(raw, self) for raw in raw_segments], 
            indices=['id', 'name'])

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
        self.account = webproperty.account
        self.id = raw['id']
        self.name = raw['name']

    def query(self, metrics=[], dimensions=[]):
        return query.CoreQuery(self, metrics=metrics, dimensions=dimensions)

    def live(self, metrics=[], dimensions=[]):
        return query.LiveQuery(self, metrics=metrics, dimensions=dimensions)

    def __repr__(self):
        return "<Profile: {} ({})>".format(
            self.name, self.id)
