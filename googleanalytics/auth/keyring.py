# encoding: utf-8

from __future__ import absolute_import

import json
import keyring


DOMAIN = 'Google Analytics API'


def get(name):
    secrets = keyring.get_password(DOMAIN, name)

    if secrets:
        return json.loads(secrets)
    else:
        return None

def set(name, secrets):
    keyring.set_password(DOMAIN, name, json.dumps(secrets))

def delete(name):
    keyring.delete_password(DOMAIN, name)
