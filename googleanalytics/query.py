from copy import copy
import collections
import addressable
import utils
import account
import columns


class Report(object):
    def __init__(self, raw, query):
        self.raw = []
        self.queries = []

        registry = query.profile.webproperty.account.columns
        headers = [registry[header['name']] for header in raw['columnHeaders']]
        slugs = [header.pyslug for header in headers]
        self.row_cls = collections.namedtuple('Row', slugs)
        self.headers = addressable.List(headers, 
            indices=registry.indexed_on, insensitive=True)
        self.rows = []
        self.append(raw, query)

    def append(self, raw, query):
        self.raw.append(raw)
        self.queries.append(query)
        self.is_complete = not 'nextLink' in raw

        casters = [column.cast for column in self.headers]

        # if no rows were returned, the GA API doesn't 
        # include the `rows` key at all
        for row in self.raw[-1].get('rows', []):
            typed_row = [casters[i](row[i]) for i in range(len(self.headers))]
            typed_tuple = self.row_cls(*typed_row)
            self.rows.append(typed_tuple)

        # TODO: figure out how this works with paginated queries
        self.totals = raw['totalsForAllResults']
        # more intuitive when querying for just a single metric
        self.total = raw['totalsForAllResults'].values()[0]
        # print self.totals

    def __getitem__(self, key):
        try:
            i = self.headers.index(key)
            return [row[i] for row in self.rows]
        except ValueError:
            raise ValueError(key + " not in column headers")

    def __iter__(self):
        raise NotImplementedError()

    def __len__(self):
        return len(self.rows)


def condition(value):
    return "condition::" + value

def sequence(value):
    return "sequence::" + value

def all(*values):
    return condition(";".join(values))

def any(*values):
    return condition(",".join(values))

def followed_by(*values):
    return sequence(";->>".join(values))

def immediately_followed_by(*values):
    return sequence(";->".join(values))


class Query(object):
    def __init__(self, profile, metrics=[], dimensions=[], meta={}):
        self.raw = {'ids': 'ga:' + profile.id}
        self.meta = {}
        self.meta.update(meta)
        self.profile = profile
        self.webproperty = profile.webproperty
        self.account = profile.webproperty.account
        self._specify(metrics=metrics, dimensions=dimensions)

    def _serialize_criterion(criterion):
        pattern = r'(?P<identifier>[\w:]+)((?P<operator>[\!\=\>\<\@\~]+)(?P<value>[\w:]+))?'
        match = re.match(pattern, criterion)
        identifier = match.group('identifier')
        operator = match.group('operator') or ''
        value = match.group('value') or ''
        column = self._serialize_column(identifier)
        return column + operator + value

    def _normalize_column(self, value):
        if isinstance(value, account.Column):
            return value
        else:
            return self.account.columns[value]

    def _serialize_column(self, value):
        return self._normalize_column(value).id

    def _serialize_columns(self, values):
        if not isinstance(values, list):
            values = [values]

        return [self._serialize_column(value) for value in values]

    def _normalize_segment(self, value):
        if isinstance(value, account.Segment):
            return value
        else:
            return self.account.segments[value]
    
    def _serialize_segment(self, value):
        return self._normalize_segment(value).id

    def _serialize(self, obj):
        if isinstance(obj, list):
            return [self._serialize(el) for el in obj]
        elif isinstance(obj, account.Column):
            return obj.id
        else:
            return obj

    def clone(self):
        query = self.__class__(profile=self.profile, meta=self.meta)
        query.raw = copy(self.raw)
        return query

    @utils.immutable
    def set(self, key=None, value=None, **kwargs):
        """
        `set` is a way to add raw properties to the request, 
        for features that python-google-analytics does not 
        support or supports incompletely. For convenience's 
        sake, it will serialize Column objects but will 
        leave any other kind of value alone.
        """

        if key and value:
            self.raw[key] = self._serialize(value)
        elif key or kwargs:
            properties = key or kwargs
            for key, value in properties.items():
                self.raw[key] = self._serialize(value)
        else:
            raise ValueError(
                "Query#set requires a key and value, a properties dictionary or keyword arguments.")

        return self

    def _specify(self, metrics=[], dimensions=[]):
        metrics = self._serialize_columns(metrics)
        dimensions = self._serialize_columns(dimensions)
        self.raw.setdefault('metrics', []).extend(metrics)
        self.raw.setdefault('dimensions', []).extend(dimensions)

        return self

    @utils.immutable
    def specify(self, *vargs, **kwargs):
        return self._specify(*vargs, **kwargs)

    @utils.immutable
    def sort(self, *columns):
        sorts = []

        for column in columns:          
            if isinstance(column, account.Column):
                ascending = False
                identifier = column.id
            elif isinstance(column, basestring):
                ascending = column.startswith('-')
                identifier = self.account.columns[column.lstrip('-')].id
            else:
                raise ValueError()

            if ascending:
                sign = '-'
            else:
                sign = ''

            sorts.append(sign + identifier) 

        self.raw['sort'] = ",".join(sorts)
        return self

    @utils.immutable
    def filter(self, value):
        """ Most of the actual functionality lives on the Column 
        object and the `all` and `any` functions. """
        self.raw['filters'] = value


class CoreQuery(Query):
    """
    TODO: 
    segment
    fields
    userIp / quotaUser
    """
    # https://developers.google.com/analytics/devguides/reporting/core/v3/reference#q_summary

    PRECISION_LEVELS = ('FASTER', 'DEFAULT', 'HIGH_PRECISION', )
    GRANULARITY_LEVELS = ('year', 'month', 'week', 'day', 'hour', )
    GRANULARITY_DIMENSIONS = (
        'ga:year', 'ga:yearMonth', 'ga:yearWeek', 
        'ga:date', 'ga:dateHour',
    )

    @utils.immutable
    def range(self, start, stop=None, months=0, days=0, precision=1, granularity=None):
        start, stop = utils.daterange(start, stop, months, days)

        self.raw.update({
            'start_date': start, 
            'end_date': stop, 
        })

        if isinstance(precision, int):
            precision = self.PRECISION_LEVELS[precision]

        if precision not in self.PRECISION_LEVELS:
            levels = ", ".join(self.PRECISION_LEVELS)
            raise ValueError("Granularity should be one of: " + levels)

        if precision != 'DEFAULT':
            self.raw.update({'samplingLevel': precision})

        if granularity:
            if not isinstance(granularity, int):
                if granularity in self.GRANULARITY_LEVELS:
                    granularity = self.GRANULARITY_LEVELS.index(granularity)
                else:
                    levels = ", ".join(options.keys())
                    raise ValueError("Granularity should be one of: " + levels)

            dimension = self.GRANULARITY_DIMENSIONS[granularity]
            self.raw['dimensions'].insert(0, dimension)

        return self

    def hourly(self, *vargs, **kwargs):
        kwargs['granularity'] = 'hour'
        return self.range(*vargs, **kwargs)

    def daily(self, *vargs, **kwargs):
        kwargs['granularity'] = 'day'
        return self.range(*vargs, **kwargs)

    def weekly(self, *vargs, **kwargs):
        kwargs['granularity'] = 'week'
        return self.range(*vargs, **kwargs)

    def monthly(self, *vargs, **kwargs):
        kwargs['granularity'] = 'month'
        return self.range(*vargs, **kwargs)

    def yearly(self, *vargs, **kwargs):
        kwargs['granularity'] = 'year'
        return self.range(*vargs, **kwargs)

    @utils.immutable
    def step(self, maximum):
        """ Specify a maximum amount of results to be returned 
        in any one request, without implying that we should stop 
        fetching beyond that limit. Useful in debugging pagination
        functionality, perhaps also when you want to be able to
        decide whether to continue fetching data, based on the data
        you've already received. """
        self.raw['max_results'] = maximum
        return self

    @utils.immutable
    def limit(self, *_range):
        """ Please not carefully that Google Analytics uses 
        1-indexing on its rows. """

        # uses the same argument order as 
        # LIMIT in a SQL database
        if len(_range) == 2:
            start, maximum = _range
        else:
            start = 1
            maximum = _range[0]

        self.meta['limit'] = maximum

        self.raw.update({
            'start_index': start, 
            'max_results': maximum, 
        })
        return self

    @utils.immutable
    def segment(self, value, type=None):
        """
        E.g.

        query.segment(account.segments['browser'])
        query.segment('browser')
        query.segment(account.segments['browser'].any('Chrome', 'Firefox'))

        You can also use the `any`, `all`, `followed_by` and 
        `immediately_followed_by` functions in this module to 
        chain together segments. (Experimental.)
        """

        # TODO / NOTE: support for dynamic segments using 
        # conditions and sequences is barebones at the moment
        if type:
            value = "{type}::{value}".format(type=type, value=value)
        else:
            value = self._serialize_segment(value)

        self.raw['segment'] = value
        return self

    def live(self):
        """ Turn a regular query into one for the live API. """
        # add in metrics, dimensions, sort, filters
        raise NotImplementedError()
        return RealTimeQuery(metrics=self.metrics, dimensions=self.dimensions)

    @utils.immutable
    def next(self):
        step = self.raw.get('max_results', 1000)
        start = self.raw.get('start_index', 1) + step
        self.raw['start_index'] = start
        return self

    def _execute(self):
        raw = copy(self.raw)
        raw['metrics'] = ','.join(self.raw['metrics'])
        raw['dimensions'] = ','.join(self.raw['dimensions'])

        service = self.account.service
        response = service.data().ga().get(**raw).execute()
        
        return Report(response, self)        

    def execute(self):
        cursor = self
        report = None
        is_complete = False
        is_enough = False

        while not (is_enough or is_complete):
            chunk = cursor._execute()

            if report:
                report.append(chunk.raw[0], cursor)
            else:
                report = chunk

            is_enough = len(report.rows) >= self.meta.get('limit', float('inf'))
            is_complete = chunk.is_complete
            cursor = cursor.next()

        return report

    def __repr__(self):
        return "<Query: {}>".format(self.profile.name)


class RealTimeQuery(Query):
    pass
    # https://developers.google.com/analytics/devguides/reporting/realtime/v3/reference/data/realtime#resource
