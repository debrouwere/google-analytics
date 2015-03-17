# encoding: utf-8

import click
import googleanalytics as ga

from .common import authenticated, cli


@cli.command()
@authenticated
def revoke(identity, accounts):
    credentials = ga.auth.identity(identity)
    ga.revoke(**credentials.serialize())
