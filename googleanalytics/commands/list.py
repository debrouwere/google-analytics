# encoding: utf-8

import re

import click

import googleanalytics as ga
from .common import authenticated, cli


def print_list(l):
    for item in l:
        click.echo(item)


@cli.command()
@click.argument('account', required=False)
@click.argument('webproperty', required=False)
@authenticated
def properties(identity, accounts, account=None, webproperty=None):
    scope = ga.auth.navigate(accounts, account, webproperty)

    if webproperty:
        print_list(scope.profiles)
    elif account:
        print_list(scope.webproperties)
    else:
        print_list(scope)


def matcher(pattern):
    def match(column):
        return re.search(pattern, column.name, re.IGNORECASE)
    return match

@cli.command()
@click.argument('account')
@click.argument('pattern', required=False)
@authenticated
def columns(identity, accounts, account, pattern=None, column_type='columns'):
    account = accounts[account]
    columns = getattr(account, column_type)

    if pattern:
        columns = filter(matcher(pattern), columns)
    
    print_list(columns)
