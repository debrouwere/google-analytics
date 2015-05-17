# Google Analytics for Python and the command-line

[![Build Status](https://travis-ci.org/debrouwere/google-analytics.svg)](https://travis-ci.org/debrouwere/google-analytics)

`google-analytics` takes the pain out of working with the Google Analytics reporting APIs. It supports both the Core and the Real Time API. It is written in Python but there's also a command-line interface.

(The goal is for the command-line interface to have feature parity with the Python interface. We're working on it.)

This package is built on top of [Google's own API client for Python](https://developers.google.com/api-client-library/python/start/installation).

* **Authentication.** OAuth2 is a bit of a pain and we've made it easier, both for interactive use and for [server applications][rauth]. We can also save your credentials in the operating system's keychain if you want to.
* **Querying.** Easier to query per week, month or year. Query using metric IDs or using their full names, whichever you think is nicer. Work with both the Core and the Real Time APIs.
* **Reporting.** Generate reports from the command-line. Optionally describe reports and queries in [easy-to-read and easy-to-write YAML files][yaml]. Reports in Python work better too: iterate through the entire report or column-per-column.
* **Exploration.** Traverse the account hierarchy from account to webproperty to profile to dimensions, both programmatically and with the included command-line interface.

[rauth]: https://github.com/debrouwere/google-analytics/blob/master/examples/server.py
[yaml]: https://github.com/debrouwere/google-analytics/blob/master/examples/query.yml

## Installation

`pip install googleanalytics` or `pip3 install googleanalytics` should do the trick.

## Authentication

...

## Querying

...

## CLI

...