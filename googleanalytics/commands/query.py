# encoding: utf-8

import json
import yaml

import click

import googleanalytics as ga
from .common import authenticated, cli


# e.g.
# 
#   googleanalytics query pageviews Fusion "Fusion (production)" "All Web Site Data" \
#       --identity fusion --start yesterday --stop yesterday

@cli.command()
@click.argument('metrics')
@click.option('--account')
@click.option('--webproperty')
@click.option('--profile')
@click.option('--dimensions')
@click.option('--start')
@click.option('--stop')
@click.option('--limit')
@click.option('--debug', is_flag=True)
@click.option('--filter', multiple=True)
@click.option('-b', '--blueprint', type=click.File('r'))
@click.option('-t', '--type', default='core', type=click.Choice(['core', 'realtime']))
@authenticated
def query(identity, accounts, metrics, 
        dimensions=None, filter=None, limit=False, 
        account=None, webproperty=None, profile=None, 
        blueprint=None, debug=False,
        **description):

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
        if not (account and webproperty):
            raise ValueError("Account and webproperty needed for query.")

        profile = ga.auth.navigate(accounts, account, webproperty, profile)
        description = {
            'type': description['type'],         
            'range': {
                'start': description['start'], 
                'stop': description['stop'],
                },
            'metrics': metrics.split(','), 
            'dimensions': (dimensions or '').split(','),  
            'filter': (filter or '').split(','), 
            'limit': int(limit) or False, 
            }
        query = ga.query.describe(profile, description)

        if debug:
            print(query.build())

        serialized_report = query.serialize()
        print(json.dumps(serialized_report, indent=4))
