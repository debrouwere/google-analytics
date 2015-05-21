# encoding: utf-8

import os
from copy import copy

import httplib2
import oauth2client
import inspector

from . import keyring
from .. import utils


def from_params(**params):
    credentials = {}
    for key, value in params.items():
        if key in ('client_id', 'client_secret', 'client_email', 'private_key', 'access_token', 'refresh_token', 'identity'):
            credentials[key] = value
    return credentials

def from_keyring(identity=None, **params):
    if identity:
        return keyring.get(identity)
    else:
        return None

def from_environment(prefix=None, suffix=None, **params):
    keys = {
        'client_id': utils.affix(prefix, 'GOOGLE_ANALYTICS_CLIENT_ID', suffix),
        'client_secret': utils.affix(prefix, 'GOOGLE_ANALYTICS_CLIENT_SECRET', suffix),
        'refresh_token': utils.affix(prefix, 'GOOGLE_ANALYTICS_REFRESH_TOKEN', suffix),
    }

    credentials = {}
    for credential, key in keys.items():
        value = os.environ.get(key)
        if value:
            credentials[credential] = value

    return credentials

def from_prompt(**params):
    prompted = {}

    if not params.get('identity'):
        prompted['identity'] = utils.input('Human-readable account name: ')
    if not params.get('client_id'):
        prompted['client_id'] = utils.input('Client ID: ')
    if not params.get('client_secret'):
        prompted['client_secret'] = utils.input('Client secret: ')

    return prompted


class Credentials(object):
    STRATEGIES = {
        'params': from_params,
        'keyring': from_keyring,
        'environment': from_environment,
        'prompt': from_prompt,
    }

    INTERACTIVE_STRATEGIES = ['params', 'keyring', 'environment', 'prompt']
    UNSUPERVISED_STRATEGIES = ['params', 'keyring', 'environment']

    @classmethod
    def find(cls, interactive=False, valid=False, complete=False, **params):
        if interactive:
            strategies = copy(cls.INTERACTIVE_STRATEGIES)
        else:
            strategies = copy(cls.UNSUPERVISED_STRATEGIES)

        attempted = ", ".join(strategies)

        credentials = cls()
        while credentials.incomplete and len(strategies):
            strategy = strategies.pop(0)
            properties = cls.STRATEGIES[strategy](**params) or {}
            for key, value in properties.items():
                if not getattr(credentials, key):
                    setattr(credentials, key, value)
                if not params.get(key):
                    params[key] = value

        # the environment variable suffix is often a good
        # descriptor of the nature of these credentials,
        # when lacking anything better
        if params.get('identity'):
            credentials.identity = params['identity']
        elif params.get('suffix') and credentials.identity is credentials.client_id:
            credentials.identity = params.get('suffix')

        if complete and credentials.incomplete:
            raise KeyError("Could not find client credentials and token. Tried {attempted}.".format(
                attempted=attempted))
        elif valid and credentials.invalid:
            raise KeyError("Could not find client id and client secret. Tried {attempted}.".format(
                attempted=attempted))
        else:
            return credentials

    def __init__(self, client_id=None, client_secret=None,
            client_email=None, private_key=None,
            access_token=None, refresh_token=None,
            identity=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.client_email = client_email
        self.private_key = private_key
        self.access_token = access_token
        self.refresh_token = refresh_token
        self._identity = identity

    @property
    def token(self):
        return self.refresh_token or self.access_token

    @property
    def identity(self):
        return self._identity or self.client_id

    @identity.setter
    def identity(self, value):
        self._identity = value

    @property
    def type(self):
        if self.client_email and self.private_key:
            return 2
        elif self.client_id and self.client_secret:
            return 3
        else:
            return None

    @property
    def valid(self):
        """ Valid credentials are not necessarily correct, but
        they contain all necessary information for an
        authentication attempt. """
        two_legged = self.client_email and self.private_key
        three_legged = self.client_id and self.client_secret
        return two_legged or three_legged or False

    @property
    def invalid(self):
        return not self.valid

    @property
    def complete(self):
        """ Complete credentials are valid and are either two-legged or include a token. """
        return self.valid and (self.access_token or self.refresh_token or self.type == 2)

    @property
    def incomplete(self):
        return not self.complete

    @property
    def oauth(self):
        if self.incomplete:
            return None
        else:
            if self.type == 2:
                return oauth2client.client.SignedJwtAssertionCredentials(
                    service_account_name=self.client_email,
                    private_key=self.private_key.encode('utf-8'),
                    scope='https://www.googleapis.com/auth/analytics.readonly',
                    )
            else:
                return oauth2client.client.OAuth2Credentials(
                    access_token=self.access_token,
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    refresh_token=self.refresh_token,
                    token_expiry=None,
                    token_uri=oauth2client.GOOGLE_TOKEN_URI,
                    user_agent=None,
                    revoke_uri=oauth2client.GOOGLE_REVOKE_URI,
                    id_token=None,
                    token_response=None
                    )

    def serialize(self):
        return {
            'identity': self.identity,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'client_email': self.client_email,
            'private_key': self.private_key,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
        }

    def authorize(self):
        return self.oauth.authorize(httplib2.Http())

    def revoke(self):
        if not self.token:
            raise KeyError("Cannot revoke a token when no token was provided.")

        # `credentials.revoke` will try to revoke the refresh token even
        # if it's None, which will fail, so we have to miss with the innards
        # of oauth2client here a little bit
        return self.oauth._do_revoke(httplib2.Http().request, self.token)


def normalize(fn):
    @inspector.changes(fn)
    def normalized_fn(client_id=None, client_secret=None,
            access_token=None, refresh_token=None, identity=None):
        
        if isinstance(client_id, Credentials):
            credentials = client_id
        else:
            credentials = Credentials(client_id, client_secret, access_token, refresh_token, identity)

        return fn(credentials)

    return normalized_fn
