"""
Convenience functions for authenticating with Google
and asking for authorization with Google, with 
`authenticate` at its core.

`authenticate` will do what it says on the tin, but unlike 
the basic `oauth.authenticate`, it also tries to get 
existing credentials from the keyring, from environment
variables, it prompts for information when required 
and so on.
"""

import credentials, keyring, oauth

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

def authenticate(client_id=None, client_secret=None, 
    access_token=None, refresh_token=None, 
    account=None, webproperty=None, profile=None, 
    identity=None, prefix=None, suffix=None, 
    interactive=False, save=False):
    
    # TODO: seeing as we're using this for both `authenticate`
    # and `authorize`, perhaps turn this first part into 
    # a decorator
    if client_id and client_secret and (access_token or refresh_token):
        creds = dict(
            client_id=client_id, 
            client_secret=client_secret, 
            access_token=access_token, 
            refresh_token=refresh_token, 
            )
    else:
        # it is possible for some but not all credentials 
        # to be present, e.g. a client id and client secret
        # from environment variables, but there's no token yet; 
        # if that's the case, we go through an authorization
        # procedure to grab a token
        creds = credentials.find(
            valid=True, 
            interactive=interactive, 
            identity=identity,
            prefix=prefix, 
            suffix=suffix, 
            )

        if credentials.are_incomplete(creds):
            if interactive:
                client_id, client_secret = credentials.client(creds)
                creds = authorize(
                    client_id=client_id, 
                    client_secret=client_secret, 
                    save=save, 
                    identity=identity or creds.get('identity'), 
                    suffix=suffix,
                    )
            else:
                raise KeyError("Could not find client id and client secret.")

    accounts = oauth.authenticate(**creds)
    scope = navigate(accounts, account=account, webproperty=webproperty, profile=profile)
    return scope

def authorize(client_id=None, client_secret=None, save=False, identity=None, prefix=None, suffix=None):
    if (client_id and client_secret):
        creds = dict(
            client_id=client_id, 
            client_secret=client_secret, 
            identity=identity, 
            )
    else:
        creds = credentials.find(
            valid=True, 
            interactive=True, 
            identity=identity,
            prefix=prefix, 
            suffix=suffix, 
            )
        client_id, client_secret = credentials.client(creds)
        identity = identity or creds.get('identity')

    if credentials.are_complete(creds):
        tokens = creds
    else:
        tokens = oauth.authorize(client_id, client_secret)

    if save:
        identity = identity or suffix or client_id
        keyring.set(identity, tokens)

    return tokens

def revoke(client_id, client_secret, access_token=None, refresh_token=None, identity=None):
    if not (access_token or refresh_token):
        creds = keyring.get(identity)
        if identity and creds:
            access_token, refresh_token = credentials.tokens(creds)
            access_token = creds['access_token']
            refresh_token = creds['refresh_token']
        else:
            raise KeyError("No token to revoke.")
    
    oauth.revoke(client_id, client_secret, access_token, refresh_token)
    keyring.delete(identity)
