Google Analytics for Python and the command-line
================================================

|Build Status|

``google-analytics`` takes the pain out of working with the Google
Analytics reporting APIs. It supports both the Core and the Real Time
API. It is written in Python but there's also a full-featured
command-line interface.

-  **Authentication.** OAuth2 is a bit of a pain and we've made it
   easier, both for interactive use and for `server
   applications <https://github.com/debrouwere/google-analytics/blob/master/examples/server.py>`__.
   We can also save your credentials in the operating system's keychain
   if you want to.
-  **Querying.** Easier to query per week, month or year. Query using
   metric IDs or using their full names, whichever you think is nicer.
   Work with both the Core and the Real Time APIs.
-  **Reporting.** Generate reports from the command-line. Optionally
   describe reports and queries in `easy-to-read and easy-to-write YAML
   files <https://github.com/debrouwere/google-analytics/blob/master/examples/query.yml>`__.
   Reports in Python work better too: iterate through the entire report
   or column-per-column.
-  **Exploration.** Traverse the account hierarchy from account to
   webproperty to profile to dimensions, both programmatically and with
   the included command-line interface.
-  **Exports.** Clean JSON and CSV – as well as
   `Pandas <http://pandas.pydata.org/>`__ data frames – so you can
   analyze the data in anything from Excel to R.

This package is built on top of `Google's own API client for
Python <https://developers.google.com/api-client-library/python/start/installation>`__.

Quickstart
----------

First, install the package using
`pip <https://pip.pypa.io/en/latest/>`__

-  Python 2: ``pip install googleanalytics``
-  Python 3: ``pip3 install googleanalytics``

Then, create a new project in the `Google Developers
Console <https://console.developers.google.com>`__, enable the Analytics
API under "APIs & auth > APIs" and generate credentials for an installed
application under "APIs & auth > Credentials". Keep this page open. For
more detail, look at the `wiki page on
authentication <https://github.com/debrouwere/google-analytics/wiki/Authentication>`__.

After that, executing your first query is as easy as

.. code:: python

    import googleanalytics as ga
    accounts = ga.authenticate()
    profile = accounts[0].webproperties[0].profile
    pageviews = profile.core.query.metrics('pageviews').range('yesterday').value
    print(pageviews)

Or on the command-line, that'd be:

.. code:: shell

    googleanalytics --identity <identity> --account <account> --webproperty <webproperty> \
        query pageviews --start yesterday

The account, webproperty and profile determine what data you'll be
querying. Learn more about profiles and querying on the
`Querying <https://github.com/debrouwere/google-analytics/wiki/Querying>`__
wiki page, or alternatively look at the `Common
Queries <https://github.com/debrouwere/google-analytics/wiki/Common-Queries>`__
page for lots of examples. Read more about how to work with the
resulting data in `Working With
Reports <https://github.com/debrouwere/google-analytics/wiki/Working-With-Reports>`__.
`On The
Command-Line <https://github.com/debrouwere/google-analytics/wiki/On-The-Command-Line>`__
has more details about the command-line application.

The example above will authorize the app and authenticate you
interactively. It is also possible to pass credentials as arguments in
Python, using environment variables or from your operating system's
keychain. Authentication is treated in much more depth on the
`authentication wiki
page <https://github.com/debrouwere/google-analytics/wiki/Authentication>`__.

.. |Build Status| image:: https://travis-ci.org/debrouwere/google-analytics.svg
   :target: https://travis-ci.org/debrouwere/google-analytics
