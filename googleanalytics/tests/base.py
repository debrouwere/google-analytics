# encoding: utf-8

import unittest

import googleanalytics as ga


class TestCase(unittest.TestCase):
    def setUp(self):
        accounts = ga.authenticate()
        if not len(accounts):
            raise Exception("Cannot proceed with unit testing: \
                the authorized Google account does not use Google Analytics.")
        else:
            self.account = accounts[0]
            self.webproperty = self.account.webproperties[0]
            self.profile = self.webproperty.profiles[0]
            self.query = self.profile.core.query