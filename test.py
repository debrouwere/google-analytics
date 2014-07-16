import os
from datetime import date
from pprint import pprint
import json
import googleanalytics as ga


# this is just a dummy app; 
# no grave danger in sharing this
client = dict(
    client_id='430195473521.apps.googleusercontent.com', 
    client_secret='4kvNSlhSdxXwaZPkFc_bJFoz'
)


def authenticate_with_tokens():
    if os.path.exists('tokens.json'):
        tokens = json.load(open('tokens.json'))
    else:
        tokens = ga.oauth.ask(**client)
        json.dump(tokens, open('tokens.json', 'w'), indent=4)

    return ga.oauth.authenticate(**tokens)

def authenticate_with_keyring():
    return ga.utils.keyring.ask_and_authenticate('dummy', **client)
    

def first(accounts):
    print accounts
    account = accounts[0]
    print account.webproperties
    print account.metrics['pageviews']
    print account.metrics['ga:pageviews']
    prop = account.webproperties[0]
    profile = prop.profiles[0]
    print profile
    return profile

def query(profile):
    # q = profile.query('pageviews').range('2014-06-01', days=3)
    # `days()` is identical to `range(granularity='day')`
    q = profile.query('pageviews').days('2014-06-01', days=4) # .limit(2) # .step(2)

    report = q.execute()

    print report.headers
    print report.rows
    print len(report.queries)
    print report['pageviews']

    #pprint(report.raw)

if __name__ == '__main__':
    accounts = authenticate_with_keyring()
    profile = first(accounts)
    query(profile)