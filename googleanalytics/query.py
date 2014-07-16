from copy import copy
import addressable
import utils
import account


class Report(object):
    def __init__(self, raw, query):
        self.raw = raw
        self.queries = []

        registry = query.profile.webproperty.account.columns
        headers = [registry[header['name']] for header in raw['columnHeaders']]
        self.headers = addressable.List(headers, indices=registry.indexed_on)
        self.rows = []
        self.append(raw, query)

    def append(self, raw, query):
        self.queries.append(query)

        casters = [column.cast for column in self.headers]
        for row in raw['rows']:
            typed_row = [casters[i](row[i]) for i in range(len(self.headers))]
            self.rows.append(typed_row)

        self.is_complete = not 'nextLink' in raw
        # TODO: figure out how this works with paginated queries
        self.totals = raw['totalsForAllResults']
        # more intuitive when querying for just a single metric
        self.total = raw['totalsForAllResults'].values()[0]

        print self.totals

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

    def clone(self):
        query = self.__class__(profile=self.profile, meta=self.meta)
        query.raw = copy(self.raw)
        return query

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
    def sort(self):
        pass

    @utils.immutable
    def filter(self):
        # filters
        pass


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

    def hours(self, *vargs, **kwargs):
        kwargs['granularity'] = 'hour'
        return self.range(*vargs, **kwargs)

    def days(self, *vargs, **kwargs):
        kwargs['granularity'] = 'day'
        return self.range(*vargs, **kwargs)

    def weeks(self, *vargs, **kwargs):
        kwargs['granularity'] = 'week'
        return self.range(*vargs, **kwargs)

    def months(self, *vargs, **kwargs):
        kwargs['granularity'] = 'month'
        return self.range(*vargs, **kwargs)

    def years(self, *vargs, **kwargs):
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
            # try to see if there's a builtin or custom (regular)
            # segment matching the supplied value
            if not isinstance(value, account.Segment):
                value = self.account.segments[value]

        self.raw['segment'] = value.id
        return self

    def live(self):
        """ Turn a regular query into one for the live API. """
        # add in metrics, dimensions, sort, filters
        raise NotImplementedError()
        return RealTimeQuery(metrics=self.metrics, dimensions=self.dimensions)

    @utils.immutable
    def next(self, start=None):
        if not start:
            step = self.raw.get('max_results', 1000)
            start = step + 1

        self.raw['start_index'] = start
        return self

    def execute(self):
        raw = copy(self.raw)
        raw['metrics'] = ','.join(self.raw['metrics'])
        raw['dimensions'] = ','.join(self.raw['dimensions'])

        service = self.account.service
        response = service.data().ga().get(**raw).execute()
        
        is_enough = self.meta.get('limit', float('inf')) < 1000
        report = Report(response, self)
        while not (is_enough or report.is_complete):
            next_query = self.next()
            next_report = next_query.execute()
            report.append(next_report.raw, next_query)
            is_enough = len(report.rows) >= self.meta.get('limit', float('inf'))

        return report

    def __repr__(self):
        return "<Query: {}>".format(self.profile.name)


class RealTimeQuery(Query):
    pass
    # https://developers.google.com/analytics/devguides/reporting/realtime/v3/reference/data/realtime#resource
