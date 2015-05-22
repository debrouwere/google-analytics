# encoding: utf-8

import json
import yaml
import click

import googleanalytics as ga
from googleanalytics import utils
from .common import cli


# TODO: maybe include an --interactive option, which defers
# to `shell` but with a prefilled query?
@cli.command()
@click.argument('metrics')
@click.option('--dimensions')
@click.option('--start')
@click.option('--stop')
@click.option('--limit')
@click.option('--sort')
@click.option('--debug',
    is_flag=True)
@click.option('--filter',
    multiple=True)
@click.option('--segment',
    multiple=True)
@click.option('--precision',
    type=click.IntRange(0, 2),
    default=1)
@click.option('-i', '--interval',
    type=click.Choice(['hour', 'day', 'week', 'month', 'year', 'lifetime']),
    default='lifetime')
@click.option('-o', '--output',
    type=click.Choice(['csv', 'json', 'ascii']),
    default='ascii')
@click.option('-b', '--blueprint',
    type=click.File('r'))
@click.option('-t', '--type',
    default='core',
    type=click.Choice(['core', 'realtime']))
@click.pass_obj
def query(scope, metrics,
        start=None, stop=None,
        dimensions=None, filter=None, limit=False, segment=None,
        blueprint=None, debug=False, output=None,
        **description):
    
    """
    e.g.

        googleanalytics query pageviews \
            --start yesterday --limit -10 --sort -pageviews \
            --dimensions pagepath \
            --identity debrouwere --account debrouwere --webproperty http://debrouwere.org \
            --debug

    """

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

        click.echo(json.dumps(reports, indent=4))
    else:
        if not isinstance(scope, ga.account.Profile):
            raise ValueError("Account and webproperty needed for query.")

        

        # LIMIT can be a plain limit or start and length
        if limit:
            limit = list(map(int, limit.split(',')))

        description.update({
            'range': {
                'start': start,
                'stop': stop,
                },
            'metrics': utils.cut(metrics, ','),
            'dimensions': utils.cut(dimensions, ','),
            'limit': limit,
            })
        query = ga.query.describe(scope, description)

        for f in filter:
            query = ga.query.refine(query, {'filter': dict(utils.cut(f, '=', ','))})

        for s in segment:
            query = ga.query.refine(query, {'segment': dict(utils.cut(s, '=', ','))})

        if debug:
            print(query.build())

        click.echo(query.serialize(format=output))
