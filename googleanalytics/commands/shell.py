# encoding: utf-8

import click

import googleanalytics as ga
from .common import authenticated, cli

try:
    from IPython import embed
except ImportError:
    import code
    def embed():
        code.interact(local=locals())

"""
profile = ga_profile()


print("* )
print("* Profile loaded into `profile`. Base query available at `base`.")
"""

@cli.command()
@click.argument('account', required=False)
@click.argument('webproperty', required=False)
@click.argument('profile', required=False)
@authenticated
def shell(identity, accounts, account=None, webproperty=None, profile=None):
    scope = ga.auth.navigate(accounts, account, webproperty, profile)
    
    if isinstance(scope, ga.account.Profile):
        profile = scope
        account = profile.account
        metrics = profile.core.metrics
        dimensions = profile.core.dimensions
        core = profile.core.query()
        realtime = profile.realtime.query()
        print('* global variables: profile, account, metrics, dimensions')
        print('* build queries with the `core` and `realtime` variables')
        print("  e.g. `core.metrics('pageviews').daily('yesterday').values`")
    else:
        print('* global variables: scope')
        print('  (provide webproperty and/or profile for additional shortcuts)')

    print()

    embed()
