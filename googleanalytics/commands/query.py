# encoding: utf-8

import json
import yaml

import click

import googleanalytics as ga
from .common import authenticated, cli


@cli.command()
@click.argument('account', required=False)
@click.argument('webproperty', required=False)
@click.argument('profile', required=False)
@click.option('-b', '--blueprint', type=click.File('r'))
@click.option('-i', '--identity')
def query(identity=None, account=None, webproperty=None, profile=None, blueprint=None):
    # profile = ga.auth.navigate(accounts, account, webproperty, profile)
    
    if blueprint:
        description = yaml.load(blueprint)
        blueprint = ga.Blueprint(description)
        credentials = {}
        credentials.update(blueprint.identity or {})
        credentials.update(blueprint.scope)
        profile = ga.authenticate(interactive=True, save=True, **credentials)
        queries = blueprint.queries(profile)

        reports = []
        for query in queries:
            report = query.get()
            reports.append({
                'title': query.title, 
                'query': query.raw, 
                'results': report.serialize(), 
            })

        click.echo(json.dumps(reports, indent=2))
    else:
        raise NotImplementedError()
