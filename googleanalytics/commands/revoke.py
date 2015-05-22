# encoding: utf-8

import click
import googleanalytics as ga

from .common import cli


@cli.command()
@click.pass_obj
def revoke(scope):
    ga.revoke(**scope.account.credentials.serialize())
