# encoding: utf-8

import click

import googleanalytics as ga
from .common import cli

try:
    from IPython import embed
except ImportError:
    import code
    def embed(local):
        code.interact(local=local)


@cli.command()
@click.pass_obj
def shell(scope):
    if isinstance(scope, ga.account.Profile):
        profile = scope
        account = profile.account
        metrics = profile.core.metrics
        dimensions = profile.core.dimensions
        core = profile.core.query
        realtime = profile.realtime.query
        print('* global variables: profile, account, metrics, dimensions')
        print('* build queries with the `core` and `realtime` variables')
        print("  e.g. `core.metrics('pageviews').daily('yesterday').values`\n")
    else:
        print('* global variables: scope')
        print('  (provide webproperty and/or profile for additional shortcuts)\n')

    embed(local=locals())
