`python-google-analytics` provides a light wrapper on top of Google's own Google Analytics API client for Python. It also includes a minimalistic command-line interface to explore your account.

* **Authentication.** OAuth2 is a bit of a pain and we've made it easier.
* **Querying.** Easier to query per week, month or year. Query using metric IDs or using their full names, whichever you think is nicer. Work with both the Core and the Live APIs.
* **Reporting.** Iterate through the entire report or column-per-column.
* **Exploration.** Traverse the account hierarchy from account to webproperty to profile to dimensions, both programmatically and with the included command-line interface.

## Authentication

The newest Google Analytics API, v3, only supports authentication using OAuth2. It won't work with your account username and password. There's a few steps to get started.

1. Go to https://console.developers.google.com/project and create a new project. This registers your application with Google.
2. Click on your project, go to `APIs & auth` and then `Credentials`.
3. Find your Client ID and Client secret. Optionally, add these to your environment variables, e.g. by adding `export GOOGLE_ANALYTICS_CLIENT_ID=...` (and so on) to your `~/.bashrc`

Now we're ready to authenticate. If you've put the client secrets in the environment, you can use these environment variables to authenticate:

    import os
    import googleanalytics as ga
    accounts = ga.oauth.ask_and_authenticate(os.environ)

`accounts` is a list of user accounts that your credentials have given you access to.

If you didn't add the client secrets to your environment variables, you can also just pass them directly from your code:

    import googleanalytics as ga
    client = dict(
        client_id='myproj.apps.googleusercontent.com', 
        client_secret='mysecret'
    )
    accounts = ga.oauth.ask_and_authenticate(**client)

### Storing credentials

If you'd like to store the OAuth2 tokens so you don't have to ask for permission every time you run your code, you can first request tokens and only later use them to authenticate, allowing you to save those tokens for later use. Here's one way that could work: 

    import googleanalytics as ga
    client = dict(
        client_id='myproj.apps.googleusercontent.com', 
        client_secret='mysecret'
    )

    if os.path.exists('tokens.json'):
        tokens = json.load(open('tokens.json'))
    else:
        tokens = ga.oauth.ask(**client)
        json.dump(tokens, open('tokens.json', 'w'), indent=4)

    accounts = ga.oauth.authenticate(**tokens)

As a convenience, we've also made it easy to store your credentials in your operating system's keychain.

    import googleanalytics as ga
    client = dict(
        client_id='myproj.apps.googleusercontent.com', 
        client_secret='mysecret'
    )

    accounts = ga.utils.keyring.ask_and_authenticate('my-app', **client)

## Querying

The querying interface looks like this.

    account = accounts[0]
    webproperty = account.webproperties[0]
    profile = webproperty.profiles[0]

    print account.metrics
    print account.dimensions
    # call metrics and other columns by their name, their full id
    # or their slug (the id without the `ga:` prefix)
    print account.metrics['pageviews'] == account.metrics['ga:pageviews']

    q = profile.query('pageviews').range('2014-06-01', days=5)
    report = q.execute()
    print report['pageviews']

Here's the basic list of methods:

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

### Querying closer to the metal

This package is still in beta and you should expect some things not to work.

In these cases, it can be useful to use the lower-level access this module provides through the `query.set` method -- you can pass set either a key and value, a dictionary with key-value pairs or you can pass keyword arguments. These will then be added to the raw query. You can always check what the raw query is going to be with the build method on queries.

    query = profile.query() \
        .set(metrics=['ga:pageviews']) \
        .set(dimensions=['ga:yearMonth']) \
        .set('start_date', '2014-07-01') \
        .set({'end_date': '2014-07-05'})

Secondly, don't forget that you can access the raw query as well as raw report data in `query.raw` and `report.raw` respectively.

    from pprint import pprint
    pprint(query.raw)
    report = query.execute()
    pprint(report.raw)

Finally, if you'd like to just use the simplified oAuth functionality in python-google-analytics, that's possible too.

    accounts = ga.oauth.authenticate(**tokens)
    raw_query = {
        'metrics': ['ga:pageviews'], 
        'dimensions': ['ga:yearMonth'], 
        'start_date': '2014-07-01', 
        'end_date': '2014-07-05', 
    }
    accounts[0].service.data().ga().get(raw_query).execute()

## CLI

`python-google-analytics` comes with a small command-line interface through the `gash` command. Use `--help` to find out more about how it works.

The command-line interface currently comes with three subcommands: 

* `auth`: get a Google Analytics OAuth token, given a client id and secret (provided as arguments, or procured from the environment)
* `revoke`: revoke existing authentication, useful for debugging or when your existing tokens for some reason don't work anymore
* `ls`: explore your account

## auth

You may specify the `client_id` and `client_secret` on the 
commandline, optionally prefaced with a short and more 
easily-remembered name for this client.

If no `client_id` and `client_secret` are specified, these 
will be fetched from your environment variables, 
by default these are in `GOOGLE_ANALYTICS_CLIENT_ID` and 
`GOOGLE_ANALYTICS_CLIENT_SECRET` but you may specify a 
suffix as the first argument to this command.

    # look in environment variables
    gash auth

    # look in `GOOGLE_ANALYTICS_CLIENT_ID_B` 
    # and `GOOGLE_ANALYTICS_CLIENT_SECRET_B`
    # environment variables
    gash auth b
    
    # specify client information on the command line
    gash auth myid mysecret

    # optionally specify a more readable client name 
    # for later reference
    gash auth mynick myid mysecret

## revoke

    gash revoke <name>

## ls

    # show all of your accounts
    gash ls myproj
    # show all of the web properties for an account
    gash ls myproj myacc
    # show all of the profiles for a web property
    gash ls myproj myacc myprop
    # show all of the columns (metrics and dimensions) for a profile
    gash ls myproj myacc myprop myprof
    gash ls myproj . . .
    # find all metrics and dimensions that have "queried" in their name
    gash ls myproj myacc . . queried