# encoding: utf-8

import json
import yaml
import click

import googleanalytics as ga
from googleanalytics import utils
from .common import authenticated, cli


# e.g.
#
#   googleanalytics query pageviews \
#     --start yesterday --limit -10 --sort -pageviews \
#     --dimensions pagepath --filter pageviews__gt=-50 \
#     --identity debrouwere --account Fusion --webproperty "Fusion (production)" \
#     --debug

@cli.command()
@click.argument('metrics')
@click.option('--account')
@click.option('--webproperty')
@click.option('--profile')
@click.option('--dimensions')
@click.option('--start')
@click.option('--stop')
@click.option('--limit')
@click.option('--sort')
@click.option('--debug', is_flag=True)
@click.option('--filter', multiple=True)
@click.option('--segment', multiple=True)
@click.option('-s', '--show', type=click.Choice(['csv', 'json', 'ascii']), default='ascii')
@click.option('-b', '--blueprint', type=click.File('r'))
@click.option('-t', '--type', default='core', type=click.Choice(['core', 'realtime']))
@authenticated
def query(identity, accounts, metrics,
        dimensions=None, filter=None, limit=False, segment=None, sort=None,
        account=None, webproperty=None, profile=None,
        blueprint=None, debug=False, show=None,
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

        # LIMIT can be a plain limit or start and length
        if limit:
            limit = list(map(int, limit.split(',')))

        description = {
            'type': description['type'],
            'range': {
                'start': description['start'],
                'stop': description['stop'],
                },
            'metrics': utils.cut(metrics, ','),
            'dimensions': utils.cut(dimensions, ','),
            'limit': limit,
            'sort': sort,
            }
        query = ga.query.describe(profile, description)

        for f in filter:
            query = ga.query.refine(query, {'filter': dict(utils.cut(f, '=', ','))})

        for s in segment:
            query = ga.query.refine(query, {'segment': dict(utils.cut(s, '=', ','))})

        if debug:
            print(query.build())

        print(query.serialize(format=show))
