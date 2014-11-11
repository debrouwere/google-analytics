import json
import click
import googleanalytics as ga
from common import authenticated, cli

@cli.command()
@click.option('-s', '--show')
@authenticated
def authorize(identity, accounts, show=False):
    credentials = ga.auth.identity(identity)

    if show:
        if show == 'pairs':
            for key, value in credentials.items():
                print key, '=', value
        else:
            print json.dumps(credentials.serialize(), indent=4)

    return credentials
