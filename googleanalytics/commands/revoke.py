# encoding: utf-8

import googleanalytics as ga
from .common import authenticated, cli


@cli.command()
@authenticated
def revoke(identity, accounts):
    ga.revoke(identity)
