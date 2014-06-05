import os
import argparse
import json
import re
import keyring
import googleanalytics as ga


DOMAIN = 'Google Analytics API'

def get_secrets(name):
    secrets = keyring.get_password(DOMAIN, name)

    if secrets:
        return json.loads(secrets)
    else:
        return None

def delete_secrets(name):
    keyring.delete_password(DOMAIN, name)

def set_secrets(name, secrets):
    keyring.set_password(DOMAIN, name, json.dumps(secrets))

def get_tokens(identifiers):
    name, client_id, client_secret = normalize_identification(identifiers)
    suffix = name.upper()
    tokens = ga.oauth.ask(client_id, client_secret, suffix=suffix)
    set_secrets(name, tokens)
    return tokens


def normalize_identification(identification):
    client_secret = False
    name = ''

    if len(identification) == 3:
        name, client_id, client_secret = identification
    if len(identification) == 2:
        client_id, client_secret = identification
        name = client_id
    elif len(identification) == 1:
        client_id = os.environ
        name = identification[0]
    elif len(identification) == 0:
        client_id = os.environ
    else:
        raise ValueError()

    return name, client_id, client_secret


def auth_command(arguments):
    get_tokens(arguments.identifiers)


def revoke_command(arguments):
    tokens = get_secrets(arguments.name)
    if tokens:
        ga.oauth.revoke(**tokens)
        delete_secrets(arguments.name)
    else:
        print 'No tokens stored; cannot revoke.'


def ls_command(arguments):
    """ analytics ls <name> <acc> <prop> <profile> <columnsearch> """

    identifiers = arguments.identifiers

    while len(identifiers) < 5:
        identifiers.append(None)

    name, account, webproperty, profile, pattern = identifiers
    tokens = get_secrets(name) or get_tokens([name])
    accounts = ga.oauth.ask_and_authenticate(**tokens)

    def print_list(l):
        for item in l:
            print item

    def match(column):
        return re.search(pattern, column.name, re.IGNORECASE)

    if pattern:
        columns = accounts[account].columns
        filtered_columns = filter(match, columns)
        print_list(filtered_columns)
    elif profile:
        columns = accounts[account].columns
        print_list(columns)
    elif webproperty:
        profiles = accounts[account].webproperties[webproperty].profiles
        print_list(profiles)
    elif account:
        webproperties = accounts[account].webproperties
        print_list(webproperties)
    else:
        print_list(accounts)


arguments = argparse.ArgumentParser()
subparsers = arguments.add_subparsers()

auth = subparsers.add_parser('auth')
auth.set_defaults(func=auth_command, 
    help="authenticate with Google Analytics")
auth.add_argument('identifiers', nargs='*')

revoke = subparsers.add_parser('revoke')
revoke.add_argument('name', default='', nargs='?')
revoke.set_defaults(func=revoke_command, 
    help="revoke Google Analytics OAuth credentials")

ls = subparsers.add_parser('ls')
ls.add_argument('identifiers', default=[''], nargs='*')
ls.set_defaults(func=ls_command, 
    help="list Google Analytics accounts, web properties, profiles and data columns")


if __name__ == '__main__':
    args = arguments.parse_args()
    args.func(args)