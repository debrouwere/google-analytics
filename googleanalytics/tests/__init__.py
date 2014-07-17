"""
These unit tests are somewhat limited in scope because they need 
to work with any Google Analytics data. Therefore, we mainly test
for coherence and whether various functions return the proper 
data structure, rather than whether the results are exactly 
such or so.
"""

import googleanalytics as ga
import unittest
import datetime
import meta, query, experimental