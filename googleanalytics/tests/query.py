# encoding: utf-8

import googleanalytics as ga
import os
import unittest
import datetime


class TestQueryingBase(unittest.TestCase):
    def setUp(self):
        accounts = ga.authenticate(
            client_id=os.environ['GOOGLE_ANALYTICS_CLIENT_ID'], 
            client_secret=os.environ['GOOGLE_ANALYTICS_CLIENT_SECRET'], 
            refresh_token=os.environ['GOOGLE_ANALYTICS_REFRESH_TOKEN'], 
            )
        if not len(accounts):
            raise Exception("Cannot proceed with unit testing: \
                the authorized Google account does not use Google Analytics.")
        else:
            self.account = accounts[0]
            self.webproperty = self.account.webproperties[0]
            self.profile = self.webproperty.profiles[0]
            self.query = self.profile.core.query

class TestQuerying(TestQueryingBase):
    def test_raw(self):
        """ It should allow people to construct raw queries. """
        a = self.query('pageviews').range('2014-07-01', '2014-07-05')
        b = self.query() \
            .set(metrics=['ga:pageviews']) \
            .set('start_date', '2014-07-01') \
            .set({'end_date': '2014-07-05'})

        self.assertEqual(a.raw, b.raw)

    def test_range_days(self):
        """ It should support various ways of defining date ranges, 
        and these will result in the correct start and end dates. """
        a = self.query('pageviews').range('2014-07-01', '2014-07-05')
        b = self.query('pageviews').range('2014-07-01', days=5)
        
        self.assertEqual(a.raw['start_date'], '2014-07-01')
        self.assertEqual(a.raw['end_date'], '2014-07-05')
        self.assertEqual(a.raw, b.raw)

    def test_range_months(self):
        """ It should support various ways of defining date ranges, 
        and these will result in the correct start and end dates. """
        a = self.query('pageviews').range('2014-07-01', '2014-08-31')
        b = self.query('pageviews').range('2014-07-01', months=2)

        self.assertEqual(a.raw['start_date'], '2014-07-01')
        self.assertEqual(a.raw['end_date'], '2014-08-31')
        self.assertEqual(a.raw, b.raw)

    def test_query(self):
        """ It should be able to run a query and return a report. """
        q = self.query('pageviews').range('2014-07-01', '2014-07-05', granularity='day')
        report = q.get()

        self.assertTrue(report.rows)

    def test_addressable_metrics(self):
        """ It should support multiple ways of pointing to a column. """
        a = self.query('pageviews')
        b = self.query('Pageviews')
        c = self.query('ga:pageviews')
        d = self.query(self.profile.core.columns['pageviews'])

        self.assertEqual(a.raw, b.raw)
        self.assertEqual(b.raw, c.raw)
        self.assertEqual(c.raw, d.raw)

    def test_query_immutable(self):
        """ It should always refine queries by creating a new query and 
        never modify the original base query. """
        a = self.query('pageviews')
        b = a.range('2014-07-01')

        self.assertNotEqual(a, b)
        self.assertNotEqual(a.raw, b.raw)

    def test_granularity(self):
        """ It should have shortcut functions that make it easier to
        define the granularity (hour, day, week, month, year) at which 
        to query should return results. """
        base = self.query('pageviews')
        a = base.range('2014-07-01', '2014-07-03').get()
        b = base.range('2014-07-01', '2014-07-03', granularity='day').get()
        c = base.daily('2014-07-01', '2014-07-03').get()

        self.assertEqual(len(a), 1)
        self.assertEqual(len(b), 3)
        self.assertNotEqual(len(a), len(b))
        self.assertEqual(len(b), len(c))

    def test_step(self):
        """ It can limit the amount of results per request. """
        q = self.query('pageviews') \
            .range('2014-07-01', '2014-07-05', granularity='day') \
            .step(2)
        report = q.get()

        self.assertEqual(len(report.queries), 3)

    def test_limit(self):
        """ It can limit the total amount of results. """
        base = self \
            .query('pageviews') \
            .range('2014-07-01', '2014-07-05', granularity='day')
        full_report = base.get()
        limited_report = base.limit(2).get()

        self.assertEqual(len(limited_report.rows), 2)
        self.assertEqual(len(limited_report), 2)
        self.assertEqual(full_report['pageviews'][:2], limited_report['pageviews'])

    def test_start_limit(self):
        """ It can limit the total amount of results as well as the 
        index at which to start. """   
        base = self \
            .query('pageviews') \
            .range('2014-07-01', '2014-07-05', granularity='day')
        full_report = base.get()
        limited_report = base.limit(2, 2).get()

        self.assertEqual(len(limited_report.rows), 2)
        self.assertEqual(len(limited_report), 2)
        self.assertEqual(full_report['pageviews'][1:3], limited_report['pageviews'])

    def test_sort(self):
        """ It can ask the Google Analytics API for sorted results. """
        q = self \
            .query('pageviews') \
            .range('2014-07-01', '2014-07-05', granularity='day')

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

    def test_cast_numbers(self):
        """ It should cast columns that contain numeric data to the 
        proper numeric types. """
        q = self.query('pageviews').daily('2014-07-01', '2014-07-02')
        report = q.get()

        for n in report['pageviews']:
            self.assertIsInstance(n, int)

    def test_cast_dates(self):
        """ It should cast columns containing dates to proper date objects. """
        q = self.query('pageviews').daily('2014-07-01', '2014-07-02')
        report = q.get()

        for date in report['date']:
            self.assertIsInstance(date, datetime.datetime)

    def test_segment_simple(self):
        """ It should support segmenting data by a segment column. """
        q = self.query('pageviews').range('2014-07-01')
        qs = q.segment('Direct Traffic')

        r = q.get()
        rs = qs.get()

        self.assertTrue(rs['pageviews'][0] <= r['pageviews'][0])

    def test_filter_simple(self):
        base = self.query('pageviews', 'ga:pagePath').range('2014-07-01')
        every = base.get()
        lt = base.filter('ga:pageviews<10').get()
        gt = base.filter('ga:pageviews>10').get()
        every = set(every['pagepath'])
        lt = set(lt['pagepath'])
        gt = set(gt['pagepath'])

        self.assertTrue(lt.issubset(every))
        self.assertTrue(gt.issubset(every))
        self.assertTrue(len(lt.intersection(gt)) == 0)


if __name__ == '__main__':
    unittest.main()