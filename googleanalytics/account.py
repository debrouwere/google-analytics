import addressable
import utils
from columns import Column, Segment
import query


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
    report = profile.query('pageviews').range('2014-10-01', '2014-10-31').execute()
    print report['pageviews']
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
            indices=['id', 'slug', 'name'], unique=is_unique, insensitive=True)

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
            indices=['id', 'name'], insensitive=True)

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
        return addressable.List(profiles, indices=['id', 'name'])        

    def query(self, *vargs, **kwargs):
        """
        A shortcut to the first profile of this webproperty.
        """
        return self.profiles[0].query(*vargs, **kwargs)

    def __repr__(self):
        return "<WebProperty: {} ({})>".format(
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

    def query(self, metrics=[], dimensions=[]):
        """
        Return a query for certain metrics and dimensions.

        ```python
        # pageviews (metric) as a function of geographical region
        profile.query('pageviews', 'region')
        # pageviews as a function of browser
        profile.query(['pageviews'], ['browser'])
        ```

        The returned query can then be further refined using 
        all methods available on the `CoreQuery` object, such as 
        `limit`, `sort`, `segment` and so on.

        Metrics and dimensions may be either strings (the column id or
        the human-readable column name) or Metric or Dimension 
        objects.

        Metrics and dimensions specified as a string are not case-sensitive.

        ```python
        profile.query
        ```

        If specifying only a single metric or dimension, you can 
        but are not required to wrap it in a list.
        """

        return query.CoreQuery(self, metrics=metrics, dimensions=dimensions)

    def live(self, metrics=[], dimensions=[]):
        """
        Return a query for certain metrics and dimensions, using the live API.

        **Note:** this is a placeholder and not implemented yet.
        """

        return query.LiveQuery(self, metrics=metrics, dimensions=dimensions)

    def __repr__(self):
        return "<Profile: {} ({})>".format(
            self.name, self.id)
