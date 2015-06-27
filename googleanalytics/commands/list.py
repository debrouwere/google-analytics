# encoding: utf-8

import re

import click
from prettytable import PrettyTable

import googleanalytics as ga
from .common import cli


def table(rows, keys):
    t = PrettyTable(keys)
    t.align = 'l'
    for row in rows:
        t.add_row(ga.utils.pick(row, keys))
    return t


# TODO: after playing around with this, it seems like a recursive view
# would actually be more useful, so you can see accounts, webproperties
# and profiles all at the same time (perhaps configurable with --depth)
@cli.command()
@click.pass_obj
def properties(scope):
    if isinstance(scope, ga.account.WebProperty):
        click.echo(table(scope.profiles, ['name', 'id']))
    elif isinstance(scope, ga.account.Account):
        click.echo(table(scope.webproperties, ['name', 'url', 'id']))
    else:
        click.echo(table(scope, ['name', 'id']))


def matcher(pattern):
    def match(column):
        return re.search(pattern, column.name, re.IGNORECASE)
    return match

@cli.command()
@click.argument('pattern', required=False)
@click.option('--realtime',
    is_flag=True,
    help='Use the RealTime API instead of the Core API.')
@click.pass_obj
def columns(scope, pattern=None, realtime=False, column_type='columns'):
    if not isinstance(scope, ga.account.Profile):
        raise ValueError('Please specify an account and webproperty.')

    if realtime:
        api = scope.realtime
    else:
        api = scope.core

    columns = getattr(api, column_type)

    if pattern:
        columns = filter(matcher(pattern), columns)
    
    click.echo(table(columns, ['name', 'slug']))
