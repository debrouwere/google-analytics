from __future__ import absolute_import
import json
import keyring
import googleanalytics as ga


DOMAIN = 'Google Analytics API'

def get(name):
    secrets = keyring.get_password(DOMAIN, name)

    if secrets:
        return json.loads(secrets)
    else:
        return None

def delete(name):
    keyring.delete_password(DOMAIN, name)

def set(name, secrets):
    keyring.set_password(DOMAIN, name, json.dumps(secrets))

def ask(name, client_id, client_secret):
    secrets = get(name)
    if secrets:
        return secrets
    else:
        suffix = name.upper()
        tokens = ga.oauth.ask(client_id, client_secret, suffix=suffix)
        set(name, tokens)
        return tokens

# analogous to `googleanalytics.oauth.ask_and_authenticate`
def ask_and_authenticate(name, client_id, client_secret):
    tokens = ask(name, client_id, client_secret)
    return ga.oauth.authenticate(**tokens)

def revoke(name):
    tokens = get(name)
    if tokens:
        ga.oauth.revoke(**tokens)
        delete(name)
    else:
        raise Exception('no tokens stored; cannot revoke')