# encoding: utf-8

import googleanalytics as ga

from . import base


class TestAuthentication(base.TestCase):
    """ Test whether the various authentication procedures work,
    whether they result in tokens, whether those tokens can be
    revoked etc. """


class TestMetaData(base.TestCase):
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