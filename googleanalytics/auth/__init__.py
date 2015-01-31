# encoding: utf-8

"""
Convenience functions for authenticating with Google
and asking for authorization with Google, with 
`authenticate` at its core.

`authenticate` will do what it says on the tin, but unlike 
the basic `googleanalytics.oauth.authenticate`, it also tries 
to get existing credentials from the keyring, from environment
variables, it prompts for information when required and so on.
"""

from . import keyring
from . import oauth
from .oauth import Flow, Credentials


def navigate(accounts, account=None, webproperty=None, profile=None):
    scope = accounts

    if account:
        scope = scope[account]

    if webproperty:
        if account:
            scope = scope.webproperties[webproperty]
        else:
            raise KeyError("Cannot navigate to a webproperty without knowing the account.")

    if profile:
        if account and webproperty:
            scope = scope.profiles[profile]
        else:
            raise KeyError("Cannot navigate to a profile without knowing account and webproperty.")

    return scope

def find(**kwargs):
    return oauth.Credentials.find(**kwargs)

def identity(name):
    return find(identity=name)

def authenticate(
        client_id=None, client_secret=None, 
        access_token=None, refresh_token=None, 
        account=None, webproperty=None, profile=None, 
        identity=None, prefix=None, suffix=None, 
        interactive=False, save=False):
    
    credentials = oauth.Credentials.find(
        valid=True,
        interactive=interactive,
        prefix=prefix,
        suffix=suffix,
        client_id=client_id, 
        client_secret=client_secret, 
        access_token=access_token, 
        refresh_token=refresh_token, 
        identity=identity,
        )

    if credentials.incomplete:
        if interactive:
            credentials = authorize(
                client_id=credentials.client_id, 
                client_secret=credentials.client_secret, 
                save=save, 
                identity=credentials.identity, 
                prefix=prefix, 
                suffix=suffix, 
                )
        else:
            raise KeyError("Cannot authenticate: enable interactive authorization or pass a token.")
    
    accounts = oauth.authenticate(credentials)
    scope = navigate(accounts, account=account, webproperty=webproperty, profile=profile)
    return scope

def authorize(client_id=None, client_secret=None, save=False, identity=None, prefix=None, suffix=None):
    base_credentials = oauth.Credentials.find(
        valid=True, 
        interactive=True, 
        identity=identity, 
        client_id=client_id, 
        client_secret=client_secret,
        prefix=prefix, 
        suffix=suffix, 
        )

    if base_credentials.incomplete:
        credentials = oauth.authorize(base_credentials.client_id, base_credentials.client_secret)
        credentials.identity = base_credentials.identity
    else:
        credentials = base_credentials

    if save:
        keyring.set(credentials.identity, credentials.serialize())

    return credentials

def revoke(client_id, client_secret, access_token=None, refresh_token=None, identity=None, prefix=None, suffix=None):
    credentials = oauth.Credentials.find(
        complete=True, 
        interactive=False, 
        identity=identity, 
        client_id=client_id, 
        client_secret=client_secret, 
        access_token=access_token, 
        refresh_token=refresh_token, 
        prefix=prefix, 
        suffix=suffix, 
        )

    retval = credentials.revoke()
    keyring.delete(credentials.identity)
    return retval
