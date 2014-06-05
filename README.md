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

## Querying

The querying interface is still being tweaked. Currently, it looks like this.

    account = accounts[0]
    webproperty = account.webproperties[0]
    profile = webproperty.profiles[0]

    print account.metrics
    print account.dimensions
    print account.metrics['pageviews'] == account.metrics['ga:pageviews']

    q = profile.query.query('pageviews').range('2014-06-01', days=5)
    print q.execute()

## CLI

`python-google-analytics` comes with a small command-line interface through the `gash` command. Use `--help` to find out more about how it works.

The command-line interface currently comes with three subcommands: 

* `auth`: get a Google Analytics OAuth token, given a client id and secret (provided as arguments, or procured from the environment)
* `revoke`: revoke existing authentication, useful for debugging or when your existing tokens for some reason don't work anymore
* `ls`: explore your account

## auth

You may specify the client_id and client_secret on the 
commandline, optionally prefaced with a short and more 
easily-remembered name for this client.

If no client_id and client_secret are specified, these 
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