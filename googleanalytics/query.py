from copy import copy
import utils
import account


class Query(object):
    def __init__(self, profile):
        self.raw = {'ids': 'ga:' + profile.id}
        self.profile = profile

    def _normalize_column(self, value):
        if isinstance(value, account.Column):
            return value
        else:
            return self.profile.webproperty.account.columns[value]

    def _serialize_column(self, value):
        return self._normalize_column(value).id

    def _serialize_columns(self, values):
        if not isinstance(values, list):
            values = [values]

        return [self._serialize_column(value) for value in values]

    def clone(self):
        query = self.__class__(self.profile)
        query.raw = copy(self.raw)
        return query

    """
    metrics
    dimensions
    sort
    filters
    start-index
    max-results
    """

    @utils.immutable
    def query(self, metrics=[], dimensions=[]):
        metrics = self._serialize_columns(metrics)
        dimensions = self._serialize_columns(dimensions)
        self.raw.setdefault('metrics', []).extend(metrics)
        self.raw.setdefault('dimensions', []).extend(dimensions)

        return self

    @utils.immutable
    def sort(self):
        pass

    @utils.immutable
    def filter(self):
        # filters
        pass

    def limit(self):
        # start-index, max-results
        pass


class CoreQuery(Query):
    """
    start-date
    end-date
    segment
    samplingLevel (DEFAULT, FASTER, HIGH_PRECISION)
    fields
    userIp / quotaUser
    """
    # https://developers.google.com/analytics/devguides/reporting/core/v3/reference#q_summary

    PRECISION_LEVELS = ['FASTER', 'DEFAULT', 'HIGH_PRECISION']
    GRANULARITY_LEVELS = ['month', 'week', 'day']

    @utils.immutable
    def range(self, start, stop=None, months=0, days=0, precision=1, granularity=2):
        start, stop = utils.daterange(start, stop, months, days)

        self.raw.update({
            'start_date': start, 
            'end_date': stop, 
        })

        # if precision not in self.PRECISION_LEVELS:
        #     levels = ", ".join(self.PRECISION_LEVELS)
        #     raise ValueError("Granularity should be one of: " + levels)

        # if granularity not in self.GRANULARITY_LEVELS:
        #     levels = ", ".join(self.GRANULARITY_LEVELS)
        #     raise ValueError("Granularity should be one of: " + levels)

        return self

    def live(self):
        # add in metrics, dimensions, sort, filters
        return RealTimeQuery()

    def execute(self):
        raw = copy(self.raw)
        raw['metrics'] = ','.join(self.raw['metrics'])
        raw['dimensions'] = ','.join(self.raw['dimensions'])

        service = self.profile.webproperty.account.service
        res = service.data().ga().get(**raw).execute()
        return res

        #self.report = Report()
        #return self.report

    def __repr__(self):
        return "<Query: {}>".format(self.profile.name)

    """
    Queries return reports with a row per unit of time.
    It should also be possible to ask for a sub-report 
    using `report[metric]` which will then pick that 
    data from each (global) row.
    """

    def __getitem__(self):
        pass

    def __iter__(self):
        if not hasattr(self, 'report'):
            self.execute()

        return self.report.__iter__()

    def __len__(self):
        if not hasattr(self, 'report'):
            self.execute()

        return self.report.__len__()


class RealTimeQuery(Query):
    pass
    # https://developers.google.com/analytics/devguides/reporting/realtime/v3/reference/data/realtime#resource
