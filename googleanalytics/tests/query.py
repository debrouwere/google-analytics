# encoding: utf-8

import googleanalytics as ga
import os
import datetime

from . import base

class TestQuerying(base.TestCase):
    def test_raw(self):
        """ It should allow people to construct raw queries. """
        a = self.query.metrics('pageviews').range('2014-07-01', '2014-07-05')
        b = self.query \
            .set(metrics=['ga:pageviews']) \
            .set('start_date', '2014-07-01') \
            .set({'end_date': '2014-07-05'})

        self.assertEqual(a.raw, b.raw)

    def test_range_days(self):
        """ It should support various ways of defining date ranges,
        and these will result in the correct start and end dates. """
        a = self.query.metrics('pageviews').range('2014-07-01', '2014-07-05')
        b = self.query.metrics('pageviews').range('2014-07-01', days=5)
        
        self.assertEqual(a.raw['start_date'], '2014-07-01')
        self.assertEqual(a.raw['end_date'], '2014-07-05')
        self.assertEqual(a.raw, b.raw)

    def test_range_months(self):
        """ It should support various ways of defining date ranges,
        and these will result in the correct start and end dates. """
        a = self.query.metrics('pageviews').range('2014-07-01', '2014-08-31')
        b = self.query.metrics('pageviews').range('2014-07-01', months=2)

        self.assertEqual(a.raw['start_date'], '2014-07-01')
        self.assertEqual(a.raw['end_date'], '2014-08-31')
        self.assertEqual(a.raw, b.raw)

    def test_query(self):
        """ It should be able to run a query and return a report. """
        q = self.query.metrics('pageviews').range('2014-07-01', '2014-07-05')
        report = q.get()

        self.assertTrue(report.rows)

    def test_addressable_metrics(self):
        """ It should support multiple ways of pointing to a column. """
        a = self.query.metrics('pageviews')
        b = self.query.metrics('Pageviews')
        c = self.query.metrics('ga:pageviews')
        d = self.query.metrics(self.profile.core.columns['pageviews'])

        self.assertEqual(a.raw, b.raw)
        self.assertEqual(b.raw, c.raw)
        self.assertEqual(c.raw, d.raw)

    def test_query_immutable(self):
        """ It should always refine queries by creating a new query and
        never modify the original base query. """
        a = self.query.metrics('pageviews')
        b = a.range('2014-07-01')

        self.assertNotEqual(a, b)
        self.assertNotEqual(a.raw, b.raw)

    def test_granularity(self):
        """ It should have shortcut functions that make it easier to
        define the granularity (hour, day, week, month, year) at which
        to query should return results. """
        base = self.query.metrics('pageviews')
        a = base.range('2014-07-01', '2014-07-03').get()
        b = base.range('2014-07-01', '2014-07-03').interval('day').get()
        c = base.daily('2014-07-01', '2014-07-03').get()

        self.assertEqual(len(a), 1)
        self.assertEqual(len(b), 3)
        self.assertNotEqual(len(a), len(b))
        self.assertEqual(len(b), len(c))

    def test_step(self):
        """ It can limit the amount of results per request. """
        q = self.query.metrics('pageviews') \
            .range('2014-07-01', '2014-07-05').interval('day') \
            .step(2)
        report = q.get()

        self.assertEqual(len(report.queries), 3)

    def test_limit(self):
        """ It can limit the total amount of results. """
        base = self \
            .query.metrics('pageviews') \
            .range('2014-07-01', '2014-07-05').interval('day')
        full_report = base.get()
        limited_report = base.limit(2).get()

        self.assertEqual(len(limited_report.rows), 2)
        self.assertEqual(len(limited_report), 2)
        self.assertEqual(full_report['pageviews'][:2], limited_report['pageviews'])

    def test_start_limit(self):
        """ It can limit the total amount of results as well as the
        index at which to start. """
        base = self \
            .query.metrics('pageviews') \
            .range('2014-07-01', '2014-07-05').interval('day')
        full_report = base.get()
        limited_report = base.limit(2, 2).get()

        self.assertEqual(len(limited_report.rows), 2)
        self.assertEqual(len(limited_report), 2)
        self.assertEqual(full_report['pageviews'][1:3], limited_report['pageviews'])

    def test_sort(self):
        """ It can ask the Google Analytics API for sorted results. """
        q = self \
            .query.metrics('pageviews') \
            .range('2014-07-01', '2014-07-05').interval('day')

        unsorted_report = q.get()
        sorted_report = q \
            .sort('pageviews').get()
        inverse_sorted_report = q \
            .sort(-self.profile.core.columns['pageviews']).get()

        self.assertEqual(inverse_sorted_report.queries[0].raw['sort'], '-ga:pageviews')
        self.assertEqual(
            set(unsorted_report['pageviews']),
            set(sorted_report['pageviews']),
        )
        self.assertEqual(
            sorted_report['pageviews'],
            inverse_sorted_report['pageviews'][::-1],
        )

    def test_sort_additive(self):
        q = self.query.metrics('pageviews').sort('pageviews').sort('sessions', descending=True).build()
        self.assertEqual(q['sort'], 'ga:pageviews,-ga:sessions')

    def test_segment_simple(self):
        """ It should support segmenting data by a segment column. """
        q = self.query.metrics('pageviews').range('2014-07-01')
        qs = q.segment('Direct Traffic')

        r = q.get()
        rs = qs.get()

        self.assertTrue(rs['pageviews'][0] <= r['pageviews'][0])

    def test_filter_string(self):
        base = self.query.metrics('pageviews').dimensions('ga:pagePath').range('2014-07-01')
        every = base.get()
        lt = base.filter('ga:pageviews<10').get()
        gt = base.filter('ga:pageviews>10').get()
        every = set(every['pagepath'])
        lt = set(lt['pagepath'])
        gt = set(gt['pagepath'])

        self.assertTrue(lt.issubset(every))
        self.assertTrue(gt.issubset(every))
        self.assertTrue(len(lt.intersection(gt)) == 0)

    def test_filter_keywords(self):
        q = self.query.metrics().filter(pageviews__lt=10).build()
        self.assertEqual(q['filters'], 'ga:pageviews<10')

    def test_filter_additive(self):
        q = self.query.metrics('pageviews').filter(medium=['cpc', 'cpm']).filter(usertype__neq='Returning User').build()
        self.assertEqual(q['filters'], 'ga:medium==cpc,ga:medium==cpm;ga:userType!=Returning User')


if __name__ == '__main__':
    unittest.main()