# encoding: utf-8

import json

import click

import googleanalytics as ga
from .common import authenticated, cli


@cli.command()
@click.option('-o', '--output', type=click.Choice(['pairs', 'json']))
@authenticated
def authorize(identity, accounts, output=False):
    credentials = ga.auth.identity(identity)

    if show:
        if show == 'pairs':
            for key, value in credentials.serialize().items():
                print(key, '=', value)
        else:
            print(json.dumps(credentials.serialize(), indent=4))

    return credentials
