# encoding: utf-8

"""
These unit tests are somewhat limited in scope because they need
to work with any Google Analytics data. Therefore, we mainly test
for coherence and whether various functions return the proper
data structure, rather than whether the results are exactly
such or so.

Before you can run these tests, create a "sandbox" project at
https://console.developers.google.com/ and run `gash auth`
to authenticate against it. Your human-readable account name
should be `pyga-unittest`.

The account you're using for these unit tests should have
at least one Google Analytics domain set up.
"""

import googleanalytics as ga
import unittest
import datetime

from . import meta, query, report
