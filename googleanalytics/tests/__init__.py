import googleanalytics as ga
import unittest
import datetime

"""
These unit tests are somewhat limited in scope because they need 
to work with any Google Analytics data. Therefore, we mainly test
for coherence and whether various functions return the proper 
data structure, rather than whether the results are exactly 
such or so.

Included are credentials to a unit testing sandbox.

The sandbox only works on localhost and while anyone can give the 
sandbox authorization to access their account, only the user 
possessing the resulting tokens can cause any misschief, not the 
sandbox owner.

The sandbox owner does see basic information about usage, such as 
the amount of queries that were run in the last day or week.
"""

client = dict(
    client_id='500839706211-8ceudrniic5b5r2i9ap3qg3am7f53g80.apps.googleusercontent.com', 
    client_secret='MFy1UAT8yInfIHCc3puf5-IX', 
)


class TestAuthentication(unittest.TestCase):
    """ Test whether the various authentication procedures work, 
    whether they result in tokens, whether those tokens can be 
    revoked etc. """


class TestMetaData(unittest.TestCase):
    """ Test whether various information about a Google Analytics
    account can be accessed: webproperties, profiles, columns, 
    metrics, dimensions, segments. """

    def _test_addressable(self):
        """ It should support multiple ways of pointing to a column. """
        a = self.account.columns['pageviews']
        b = self.account.columns['Pageviews']
        c = self.account.columns['ga:pageviews']

        self.assertEqual(a, b)
        self.assertEqual(b, c)


class TestQuerying(unittest.TestCase):
    def setUp(self):
        domain = 'pyga-unittest'
        accounts = ga.utils.keyring.ask_and_authenticate(domain, **client)
        if not len(accounts):
            raise Exception("Cannot proceed with unit testing: \
                the authorized Google account does not use Google Analytics.")
        else:
            self.account = accounts[0]
            self.webproperty = self.account.webproperties[0]
            self.profile = self.webproperty.profiles[0]
            self.query = self.profile.query

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
        report = q.execute()

        self.assertTrue(report.rows)

    def test_addressable_metrics(self):
        """ It should support multiple ways of pointing to a column. """
        a = self.query('pageviews')
        b = self.query('Pageviews')
        c = self.query('ga:pageviews')
        d = self.query(self.account.columns['pageviews'])

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
        a = base.range('2014-07-01', '2014-07-03').execute()
        b = base.range('2014-07-01', '2014-07-03', granularity='day').execute()
        c = base.days('2014-07-01', '2014-07-03').execute()

        self.assertEqual(len(a), 1)
        self.assertEqual(len(b), 3)
        self.assertNotEqual(len(a), len(b))
        self.assertEqual(len(b), len(c))

    def test_step(self):
        """ It can limit the amount of results per request. """
        q = self.query('pageviews') \
            .range('2014-07-01', '2014-07-05', granularity='day') \
            .step(2)
        report = q.execute()

        self.assertEqual(len(report.queries), 3)

    def test_limit(self):
        """ It can limit the total amount of results. """
        base = self \
            .query('pageviews') \
            .range('2014-07-01', '2014-07-05', granularity='day')
        full_report = base.execute()
        limited_report = base.limit(2).execute()

        self.assertEqual(len(limited_report.rows), 2)
        self.assertEqual(len(limited_report), 2)
        self.assertEqual(full_report['pageviews'][:2], limited_report['pageviews'])

    def test_start_limit(self):
        """ It can limit the total amount of results as well as the 
        index at which to start. """   
        base = self \
            .query('pageviews') \
            .range('2014-07-01', '2014-07-05', granularity='day')
        full_report = base.execute()
        limited_report = base.limit(2, 2).execute()

        self.assertEqual(len(limited_report.rows), 2)
        self.assertEqual(len(limited_report), 2)
        self.assertEqual(full_report['pageviews'][1:3], limited_report['pageviews'])

    def test_cast_numbers(self):
        """ It should cast columns that contain numeric data to the 
        proper numeric types. """
        q = self.query('pageviews').days('2014-07-01', '2014-07-02')
        report = q.execute()

        for n in report['pageviews']:
            self.assertIsInstance(n, int)

    def test_cast_dates(self):
        """ It should cast columns containing dates to proper date objects. """
        q = self.query('pageviews').days('2014-07-01', '2014-07-02')
        report = q.execute()

        for date in report['date']:
            self.assertIsInstance(date, datetime.datetime)

    def test_segment_simple(self):
        """ It should support segmenting data by a segment column. """
        q = self.query('pageviews').range('2014-06-01')
        qs = q.segment('Direct Traffic')

        r = q.execute()
        rs = qs.execute()

        self.assertTrue(rs['pageviews'][0] <= r['pageviews'][0])


if __name__ == '__main__':
    unittest.main()