# encoding: utf-8

import googleanalytics as ga
import datetime

from . import base


class TestReporting(base.TestCase):
    def test_tuples(self):
        """ It should parse analytics responses into named tuples with the correct column names. """
        report = self.query.metrics('pageviews', 'sessions').dimensions('pagepath').range('yesterday').get()
        row = report.rows[0]
        self.assertEqual(row._fields, ('page_path', 'pageviews', 'sessions'))

    def test_shortcuts(self):
        """ It should have shortcuts to grab the first and last row.
        It should have shortcuts to grab the first or all values of a one-metric query. """
        report = self.query.metrics('pageviews').range('yesterday').get()
        self.assertEqual(report.first, report.rows[0])
        self.assertEqual(report.last, report.rows[-1])
        self.assertEqual(report.values, [report.rows[0].pageviews])
        self.assertEqual(report.value, report.rows[0].pageviews)

    def test_columnwise(self):
        """ It should have the ability to extract a particular column of data. """
        report = self.query.metrics('pageviews').dimensions('pagepath').daily(days=-10).get()
        self.assertEqual(report['pagepath'], [row.page_path for row in report.rows])

    def test_serialization(self):
        """ serialized rows """
        serialized = self.query.metrics('pageviews', 'sessions').daily(days=-10).serialize()
        for row in serialized:
            self.assertTrue(set(row.keys()) == set(['date', 'pageviews', 'sessions']))

    def test_cast_numbers(self):
        """ It should cast columns that contain numeric data to the
        proper numeric types. """
        q = self.query.metrics('pageviews').daily('2014-07-01', '2014-07-02')
        report = q.get()

        for n in report['pageviews']:
            self.assertIsInstance(n, int)

    def test_cast_dates(self):
        """ It should cast columns containing dates to proper date objects. """
        q = self.query.metrics('pageviews').daily('2014-07-01', '2014-07-02')
        report = q.get()

        for date in report['date']:
            self.assertIsInstance(date, datetime.date)
