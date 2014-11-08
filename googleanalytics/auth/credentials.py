"""
Try to find credentials using a whole range of strategies.

TODO: a more OO approach would make for a nicer interface

    Credentials.find
               #valid
               #complete
               #client
               #tokens

and then

    from credentials import Credentials

"""

import os
from googleanalytics import utils
import keyring

# valid credentials are not necessarily correct, but 
# they contain all necessary information for an 
# authentication attempt
def are_valid(credentials):
    return 'client_id' in credentials and 'client_secret' in credentials

def are_invalid(credentials):
    return not are_valid(credentials)

def are_complete(credentials):
    has_client = are_valid(credentials)
    has_token = 'access_token' in credentials or 'refresh_token' in credentials
    return has_client and has_token

def are_incomplete(credentials):
    return not are_complete(credentials)

def from_keyring(identity=None, **kwargs):
    return keyring.get(identity)

def from_environment(prefix=None, suffix=None, **kwargs):
    keys = {
        "client_id": utils.affix(prefix, 'GOOGLE_ANALYTICS_CLIENT_ID', suffix), 
        "client_secret": utils.affix(prefix, 'GOOGLE_ANALYTICS_CLIENT_SECRET', suffix), 
        "refresh_token": utils.affix(prefix, 'GOOGLE_ANALYTICS_REFRESH_TOKEN', suffix),       
    }

    credentials = {}
    for credential, key in keys.items():
        value = os.environ.get(key)
        if value:
            credentials[credential] = value

    return credentials

def from_prompt(**kwargs):
    return {
        'identity': raw_input('Human-readable account name: '), 
        'client_id': raw_input('Client ID: '), 
        'client_secret': raw_input('Client secret: '), 
    }

STRATEGIES = {
    'keyring': from_keyring, 
    'environment': from_environment, 
    'prompt': from_prompt, 
}

def find(interactive=False, valid=False, complete=False, **kwargs):
    if interactive:
        strategies = ['keyring', 'environment', 'prompt']
    else:
        strategies = ['keyring', 'environment']

    attempted = ", ".join(strategies)

    credentials = {}
    while are_invalid(credentials) and len(strategies):
        strategy = strategies.pop(0)
        properties = STRATEGIES[strategy](**kwargs) or {}
        for key, value in properties.items():
            credentials.setdefault(key, value)

    if complete and are_incomplete(credentials):
        raise KeyError("Could not find client credentials and token. Tried {attempted}.".format(
            attempted=attempted))
    elif valid and are_invalid(credentials):
        raise KeyError("Could not find client id and client secret. Tried {attempted}.".format(
            attempted=attempted))
    else:
        return credentials

def client(credentials):
    client_id = credentials['client_id']
    client_secret = credentials['client_secret']
    return (client_id, client_secret)

def tokens(credentials):
    access_token = credentials['access_token']
    refresh_token = credentials['refresh_token']
    return (access_token, refresh_token)
