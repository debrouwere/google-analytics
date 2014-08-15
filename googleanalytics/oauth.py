import json
import httplib2
import argparse
import webbrowser
import addressable
import oauth2client
from oauth2client import client
from apiclient import discovery
import utils
import account


class Flow(client.OAuth2WebServerFlow):
    def __init__(self, client_id, client_secret, redirect_uri):
        super(Flow, self).__init__(client_id, client_secret, 
            scope='https://www.googleapis.com/auth/analytics.readonly', 
            redirect_uri=redirect_uri)

    def step2_exchange(self, code):
        credentials = super(Flow, self).step2_exchange(code)
        return serialize_credentials(credentials)


def credentials_from_tokens(client_id, client_secret, access_token=None, refresh_token=None):
    return client.OAuth2Credentials(
        access_token=access_token,
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        token_expiry=None,
        token_uri=oauth2client.GOOGLE_TOKEN_URI,
        user_agent=None,
        revoke_uri=oauth2client.GOOGLE_REVOKE_URI,
        id_token=None,
        token_response=None
        )


def serialize_credentials(credentials):
    return {
        'client_id': credentials.client_id, 
        'client_secret': credentials.client_secret, 
        'access_token': credentials.access_token, 
        'refresh_token': credentials.refresh_token, 
    }


def normalize_client_secrets(client_id, client_secret, prefix='', suffix=''):
    # if no client_secret is specified, we will assume that instead 
    # we have received a dictionary with credentials (such as
    # from os.environ)
    if not client_secret:
        source = client_id
        key_to_id = utils.affix(prefix, 'GOOGLE_ANALYTICS_CLIENT_ID', suffix)
        key_to_secret = utils.affix(prefix, 'GOOGLE_ANALYTICS_CLIENT_SECRET', suffix)
        client_id = source[key_to_id]
        client_secret = source[key_to_secret]

    return client_id, client_secret


# a simplified version of `oauth2client.tools.run_flow`
def ask(client_id, client_secret=None, access_token=None, refresh_token=None, port=5000, prefix='', suffix=''):
    if access_token or refresh_token:
        return {
            'client_id': client_id, 
            'client_secret': client_secret, 
            'access_token': access_token, 
            'refresh_token': refresh_token, 
        }

    client_id, client_secret = normalize_client_secrets(client_id, client_secret, prefix, suffix)
    flow = Flow(client_id, client_secret, 
        redirect_uri='http://localhost:{port}/'.format(port=port))

    authorize_url = flow.step1_get_authorize_url()
    webbrowser.open(authorize_url, new=1, autoraise=True)
    qs = utils.single_serve(
        message='Authentication flow completed. You may close the browser tab.', 
        port=port)
    return flow.step2_exchange(qs['code'])    


def revoke(client_id, client_secret, access_token=None, refresh_token=None):
    credentials = credentials_from_tokens(
        client_id, client_secret, access_token, refresh_token)

    # `credentials.revoke` will try to revoke the refresh token even 
    # if it's None, which will fail, so we have to miss with the innards
    # of oauth2client here a little bit
    if refresh_token:
        token = refresh_token
    else:
        token = access_token

    credentials._do_revoke(httplib2.Http().request, token)


def authenticate(client_id, client_secret, access_token=None, refresh_token=None):
    if not (access_token or refresh_token):
        raise ValueError("Access or refresh token required.")

    credentials = credentials_from_tokens(
        client_id, client_secret, access_token, refresh_token)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('analytics', 'v3', http=http)
    raw_accounts = service.management().accounts().list().execute()['items']
    accounts = [account.Account(raw, service) for raw in raw_accounts]
    return addressable.List(accounts, indices=['id', 'name'])


def ask_and_authenticate(*vargs, **kwargs):
    tokens = ask(*vargs, **kwargs)
    return authenticate(**tokens)
