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

For Python 3, you might need to grab the latest version of the httplib2 from GitHub, as the PyPI version is out of date. Try `pip3 install git+https://github.com/jcgregorio/httplib2`.

## Authentication

The newest Google Analytics API, v3, only supports authentication using OAuth2. It won't work with your account username and password. There's a few steps to get started.

1. Go to https://console.developers.google.com/project and create a new project. This registers your application with Google.
2. Click on your project, go to `APIs & auth` and then `Credentials`.
3. Find your Client ID and Client secret or generate new ones. (If you need to generate new credentials, ask for offline use.) Optionally, add these credentials to your environment variables, e.g. by adding `export GOOGLE_ANALYTICS_CLIENT_ID=...` (and so on) to your `~/.zshrc` or `~/.bashrc`

Now we're ready to authorize and authenticate.

On the command-line, type:

```shell
googleanalytics authorize --identity myproject
```

`google-analytics` will look through your environment variables and your operating system's keychain for existing credentials. If nothing's there, you will be prompted for a client id and client secret, and then asked to authorize the command-line interface to access to your analytics data.

Alternatively, in Python: 

```python
import googleanalytics as ga
accounts = ga.authenticate()
```

`accounts` is a list of user accounts that your credentials have given you access to.

If you already know which account, web property and profile you'd like to access, you can tell `ga.authenticate` to return the correct profile rather than a list of all accounts:

```python
import googleanalytics as ga
profile = ga.authenticate(
    account='debrouwere.org', 
    webproperty='http://debrouwere.org', 
    profile='debrouwere.org'
    )
report = profile.query('pageviews').range('2014-10-01', '2014-10-31').get()
print report['pageviews']
```

If you didn't add the client secrets to your environment variables, you can also just pass them directly from your code, though it's not always the safest option:

```python
import googleanalytics as ga
client = dict(
    client_id='myproj.apps.googleusercontent.com', 
    client_secret='mysecret'
)
accounts = ga.authenticate(**client)
```

### Storing credentials

If you'd like to store the OAuth2 tokens so you don't have to ask for permission every time you run your code, you absolutely can. On the command-line, this is the default behavior: once authenticated, we save your credentials. In Python, pass `save=True` and `interactive=True`: 

```python
import googleanalytics as ga
accounts = ga.authenticate(save=True, interactive=True)
```

If you'd prefer saving `client_id`, `client_secret` and `refresh_token` somewhere yourself,  that's possible too:

```python
import os
import json
import googleanalytics as ga
if os.exists('credentials.json'):
    credentials = json.parse(open('credentials.json'))
else:
    # authorize your code to access the Google Analytics API
    # (this will be interactive, as you'll need to confirm
    # in a browser window)
    credentials = ga.authorize()
    # turn the credentials object into a plain dictionary
    credentials = credentials.serialize()
    json.dump(credentials, open('credentials.json', 'w'))

ga.authenticate(**credentials)
```

## Querying

The querying interface looks like this.

```python
account = accounts[0]
webproperty = account.webproperties[0]
profile = webproperty.profiles[0]

print profile.core.metrics
print profile.realtime.metrics
print profile.core.dimensions
print profile.realtime.dimensions
# call metrics and other columns by their name, their full id
# or their slug (the id without the `ga:` prefix)
print profile.core.metrics['pageviews'] == profile.core.metrics['ga:pageviews']

q = profile.core.query('pageviews').range('2014-06-01', days=5)
report = q.get()
print report['pageviews']
```

Here's the basic list of methods for the Core Reporting API:

    query
        .sort
        .filter
        .range
        .hourly
        .daily
        .weekly
        .monthly
        .yearly
        .limit
        .segment

More [detailed information is available in the wiki](https://github.com/debrouwere/google-analytics/wiki/Interface).

### Querying closer to the metal

This package is still in beta and you should expect some things not to work.

In these cases, it can be useful to use the lower-level access this module provides through the `query.set` method -- you can pass set either a key and value, a dictionary with key-value pairs or you can pass keyword arguments. These will then be added to the raw query. You can always check what the raw query is going to be with the build method on queries.

```python
query = profile.core.query() \
    .set(metrics=['ga:pageviews']) \
    .set(dimensions=['ga:yearMonth']) \
    .set('start_date', '2014-07-01') \
    .set({'end_date': '2014-07-05'})
```

Secondly, don't forget that you can access the raw query as well as raw report data in `query.raw` and `report.raw` respectively.

```python
from pprint import pprint
pprint(query.raw)
report = query.get()
pprint(report.raw)
```

Finally, if you'd like to just use the simplified oAuth functionality in python-google-analytics, that's possible too, using Google's `service` interface on the `Account` object.

```python
accounts = ga.authenticate()
raw_query = {
    'ids': 'ga:26206906', 
    'metrics': ['ga:pageviews'], 
    'dimensions': ['ga:yearMonth'], 
    'start_date': '2014-07-01', 
    'end_date': '2014-07-05', 
}
accounts[0].service.data().ga().get(raw_query).execute()
```

### Using the Real Time Reporting API

The [Real Time Reporting API][realtime] is currently in closed beta. However, you can [request access][realtime/access] by filling out a short form and will generally be granted access to the API within 24 hours.

The Real Time API is very similar to the Core API:

```python
import googleanalytics
accounts = googleanalytics.authenticate(identity='me')
profile = accounts[0].webproperties[0].profiles[0]
# Core API
profile.core.query('pageviews').daily('3daysAgo').values
# Real Time API
profile.realtime.query('pageviews', 'minutes ago').values
```

The only caveat is that not all of the metrics and dimensions you're used to from the Core are supported. Take a look at the [Real Time Reporting API reference documentation][realtime/reference] to find out more, or check out all available columns interactively through `Profile#realtime.metrics` and `Profile#realtime.dimensions` in Python.

[realtime/access]:https://docs.google.com/forms/d/1qfRFysCikpgCMGqgF3yXdUyQW4xAlLyjKuOoOEFN2Uw/viewform
[realtime/reference]:https://developers.google.com/analytics/devguides/reporting/realtime/dimsmets/

## CLI

`python-google-analytics` comes with a command-line interface: the `googleanalytics` command. Use `--help` to find out more about how it works.

The command-line interface currently comes with four subcommands: 

* `authorize`: get a Google Analytics OAuth token, given a client id and secret (provided as arguments, or procured from the environment)
* `revoke`: revoke existing authentication, useful for debugging or when your existing tokens for some reason don't work anymore
* `properties`: explore your account
* `columns`: see what metrics, dimensions, segments et cetera are present

## auth

You may specify the `client_id` and `client_secret` on the commandline, optionally prefaced with a short and more easily-remembered name for this client.

If no `client_id` and `client_secret` are specified, these will be fetched from your environment variables or you will be prompted to enter them.

```shell
# look in environment variables, or prompt the user
googleanalytics authorize

# look in `GOOGLE_ANALYTICS_CLIENT_ID_DEBROUWERE` 
# and `GOOGLE_ANALYTICS_CLIENT_SECRET_DEBROUWERE`
# environment variables, and save credentials 
# under `debrouwere` in the keychain
googleanalytics authorize debrouwere

# specify client information on the command line
gash authorize debrouwere myid mysecret
```

## revoke

Revoke access to your account. You'll have to `authorize` again before `google-analytics` will be able to work with your data.

```shell
googleanalytics revoke debrouwere
```

## properties

```shell
# show all of your accounts
googleanalytics properties --identity debrouwere
# show all of the web properties for an account
googleanalytics properties debrouwere --identity debrouwere
# show all of the profiles for a web property
googleanalytics properties debrouwere http://debrouwere.org  --identity debrouwere
```

## columns

```shell
# show all of the columns (metrics and dimensions) for a profile
googleanalytics columns --identity debrouwere
# find all metrics and dimensions that have "queried" or "pageviews" in their name
googleanalytics columns queried --identity debrouwere
googleanalytics columns pageviews --identity debrouwere
```
