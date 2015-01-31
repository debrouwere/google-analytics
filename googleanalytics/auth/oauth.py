# encoding: utf-8

import json
import webbrowser

import addressable
from oauth2client import client
from apiclient import discovery

from googleanalytics import utils, account
from .credentials import Credentials, normalize


class Flow(client.OAuth2WebServerFlow):
    def __init__(self, client_id, client_secret, redirect_uri):
        super(Flow, self).__init__(client_id, client_secret, 
            scope='https://www.googleapis.com/auth/analytics.readonly', 
            redirect_uri=redirect_uri)

    def step2_exchange(self, code):
        credentials = super(Flow, self).step2_exchange(code)
        return Credentials.find(complete=True, **credentials.__dict__)

# a simplified version of `oauth2client.tools.run_flow`
def authorize(client_id, client_secret, port=5000):
    flow = Flow(client_id, client_secret, 
        redirect_uri='http://localhost:{port}/'.format(port=port))

    authorize_url = flow.step1_get_authorize_url()
    webbrowser.open(authorize_url, new=1, autoraise=True)
    qs = utils.single_serve(
        message='Authentication flow completed. You may close the browser tab.', 
        port=port)
    return flow.step2_exchange(qs['code'])    

@normalize
def revoke(credentials):
    return credentials.revoke()

@normalize
def authenticate(credentials):
    client = credentials.authorize()
    service = discovery.build('analytics', 'v3', http=client)
    raw_accounts = service.management().accounts().list().execute()['items']
    accounts = [account.Account(raw, service) for raw in raw_accounts]
    return addressable.List(accounts, indices=['id', 'name'], insensitive=True)
