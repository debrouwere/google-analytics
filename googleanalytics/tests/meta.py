import googleanalytics as ga
import unittest
import datetime
from secrets import client


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


if __name__ == '__main__':
    unittest.main()