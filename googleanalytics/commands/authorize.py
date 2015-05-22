# encoding: utf-8

import json

import click

import googleanalytics as ga
from .common import cli


@cli.command()
@click.option('-o', '--output', type=click.Choice(['kv', 'json']))
@click.pass_obj
def authorize(scope, output=False):
    credentials = scope.account.credentials

    if output:
        if output == 'kv':
            click.echo(ga.utils.paste(credentials.serialize().items(), ' = ', '\n'))
        else:
            click.echo(json.dumps(credentials.serialize(), indent=4))

    return credentials
