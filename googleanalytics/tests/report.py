# encoding: utf-8

import googleanalytics as ga
import datetime

from . import base


class TestReporting(base.TestCase):
    def _test_tuples(self):
        """ correct column names for tuples """

    def _test_shortcuts(self):
        """ first, last, value, values """

    def _test_rowwise(self):
        """ report.rows """

    def _test_columnwise(self):
        """ report['col'] """

    def _test_serialization(self):
        """ serialized rows """

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
