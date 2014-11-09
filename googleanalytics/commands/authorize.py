import json
import click
import googleanalytics as ga
from common import authenticated, cli

@cli.command()
@click.option('-s', '--show', is_flag=True)
@authenticated
def authorize(identity, accounts, show=False):
    credentials = ga.auth.identity(identity)

    if show: 
        print json.dumps(credentials.serialize(), indent=4)

    return credentials
