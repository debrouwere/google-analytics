# encoding: utf-8

"""
"""

import functools

import yaml
import addressable

from . import utils
from . import query
from . import columns
from .columns import Column, Segment, ColumnList, SegmentList


class Account(object):
    """
    An account is usually but not always associated with a single 
    website. It will often contain multiple web properties 
    (different parts of your website that you've configured
    Google Analytics to analyze separately, or simply the default
    web property that every website has in Google Analytics), 
    which in turn will have one or more profiles.

    You should navigate to a profile to run queries.

    ```python
    import googleanalytics as ga
    accounts = ga.authenticate()
    profile = accounts['debrouwere.org'].webproperties['UA-12933299-1'].profiles['debrouwere.org']
    report = profile.core.query('pageviews').range('2014-10-01', '2014-10-31').execute()
    print(report['pageviews'])
    ```
    """

    def __init__(self, raw, service):
        self.service = service
        self.raw = raw
        self.id = raw['id']
        self.name = raw['name']
        self.permissions = raw['permissions']['effective']

    @property
    @utils.memoize
    def webproperties(self):
        """
        A list of all web properties on this account. You may 
        select a specific web property using its name, its id 
        or an index.

        ```
        account.webproperties[0]
        account.webproperties['UA-9234823-5']
        account.webproperties['debrouwere.org']
        ```
        """

        raw_properties = self.service.management().webproperties().list(
            accountId=self.id).execute()['items']
        _webproperties = [WebProperty(raw, self) for raw in raw_properties]
        return addressable.List(_webproperties, indices=['id', 'name'], insensitive=True)

    @property
    def query(self, *vargs, **kwargs):
        """ A shortcut to the first profile of the first webproperty. """
        return self.webproperties[0].query(*vargs, **kwargs)

    def __repr__(self):
        return "<googleanalytics.account.Account object: {} ({})>".format(
            self.name, self.id)


class WebProperty(object):
    """
    A web property is a particular website you're tracking in Google Analytics.
    It has one or more profiles, and you will need to pick one from which to 
    launch your queries.
    """

    def __init__(self, raw, account):
        self.account = account
        self.raw = raw
        self.id = raw['id']
        self.name = raw['name']
        # on rare occassions, e.g. for abandoned web properties, 
        # a website url might not be present
        self.url = raw.get('websiteUrl')

    @property
    @utils.memoize
    def profiles(self):
        """
        A list of all profiles on this web property. You may 
        select a specific profile using its name, its id 
        or an index.

        ```
        property.profiles[0]
        property.profiles['9234823']
        property.profiles['marketing profile']
        ```
        """
        raw_profiles = self.account.service.management().profiles().list(
            accountId=self.account.id,
            webPropertyId=self.id).execute()['items']
        profiles = [Profile(raw, self) for raw in raw_profiles]
        return addressable.List(profiles, indices=['id', 'name'], insensitive=True)        

    def query(self, *vargs, **kwargs):
        """
        A shortcut to the first profile of this webproperty.
        """
        return self.profiles[0].query(*vargs, **kwargs)

    def __repr__(self):
        return "<googleanalytics.account.WebProperty object: {} ({})>".format(
            self.name, self.id)


class Profile(object):
    """
    A profile is a particular analytics configuration of a web property.
    Each profile belongs to a web property and an account. As all 
    queries using the Google Analytics API run against a particular
    profile, queries can only be created from a `Profile` object.

    ```python
    profile.query('pageviews').range('2014-01-01', days=7).execute()
    ```
    """

    def __init__(self, raw, webproperty):
        self.raw = raw
        self.webproperty = webproperty
        self.account = webproperty.account
        self.id = raw['id']
        self.name = raw['name']
        self.core = CoreReportingAPI(self)
        self.realtime = RealTimeReportingAPI(self)

    def __repr__(self):
        return "<googleanalytics.account.Profile object: {} ({})>".format(
            self.name, self.id)


class ReportingAPI(object):
    REPORT_TYPES = {
        'ga': 'ga', 
        'realtime': 'rt', 
    }

    QUERY_TYPES = {
        'ga': query.CoreQuery, 
        'realtime': query.RealTimeQuery, 
    }

    def __init__(self, endpoint, profile):
        """
        Endpoint can be one of `ga` or `realtime`.
        """
        
        # various shortcuts
        self.profile = profile
        self.account = account = profile.account
        self.service = service = profile.account.service
        root = service.data()
        self.endpoint_type = endpoint
        self.endpoint = getattr(root, endpoint)()

        # query interface 
        self.report_type = self.REPORT_TYPES[endpoint]
        self.query = functools.partial(self.QUERY_TYPES[endpoint], self)

    @property
    @utils.memoize
    def columns(self):
        return addressable.filter(columns.is_supported, self.all_columns)

    @property
    @utils.memoize
    def all_columns(self):
        query = self.service.metadata().columns().list(
            reportType=self.report_type
            )
        raw_columns = query.execute()['items']
        hydrated_columns = utils.flatten(map(Column.from_metadata, raw_columns))
        return ColumnList(hydrated_columns, unique=False)

    @property
    @utils.memoize
    def segments(self):
        query = self.service.management().segments().list()
        raw_segments = query.execute()['items']
        hydrated_segments = [Segment(raw, self) for raw in raw_segments]
        return SegmentList(hydrated_segments)

    @property
    @utils.memoize
    def metrics(self):
        return addressable.filter(columns.is_metric, self.columns)

    @property
    @utils.memoize
    def dimensions(self):
        return addressable.filter(columns.is_dimension, self.columns)

    @property
    @utils.memoize
    def goals(self):
        raise NotImplementedError()

    def __repr__(self):
        return '<googleanalytics.account.{} object>'.format(self.__class__.__name__)


class CoreReportingAPI(ReportingAPI):
    def __init__(self, profile):
        super(CoreReportingAPI, self).__init__('ga', profile)


class RealTimeReportingAPI(ReportingAPI):
    def __init__(self, profile):
        super(RealTimeReportingAPI, self).__init__('realtime', profile)

    # in principle, we should be able to reuse everything from the ReportingAPI
    # base class, but the Real Time Reporting API is still in beta and some 
    # things – like a metadata endpoint – are missing.
    @property
    @utils.memoize
    def all_columns(self):
        raw_columns = yaml.load(open(utils.here('realtime.yml')))
        hydrated_columns = [Column(item, self) for item in raw_columns]
        return ColumnList(hydrated_columns)
