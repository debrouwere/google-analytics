# encoding: utf-8

import json
import yaml
import click

import googleanalytics as ga
from googleanalytics import utils
from .common import cli


# TODO: the blueprint stuff can probably be simplified so that
# it's little more than just a call to ga.describe
def from_blueprint(scope, src):
    description = yaml.load(src)
    blueprint = ga.Blueprint(description)
    credentials = {}
    credentials.update(blueprint.identity or {})
    credentials.update(blueprint.scope)
    profile = ga.authenticate(interactive=True, save=True, **credentials)
    return blueprint.queries(profile)


# TODO: add any query generation improvements not associated with
# string parsing back into blueprint generation and query.refine
# so they apply across the board
def from_args(scope, metrics,
        start, stop, days, limit,
        dimensions, filter, segment,
        **description):

    # LIMIT can be a plain limit or start and length
    if limit:
        limit = list(map(int, limit.split(',')))

    description.update({
        'range': {
            'start': start,
            'stop': stop,
            'days': days,
            },
        'metrics': utils.cut(metrics, ','),
        'limit': limit,
        })

    if dimensions:
        description['dimensions'] = utils.cut(dimensions, ',')

    query = ga.query.describe(scope, description)

    for f in filter:
        query = ga.query.refine(query, {'filter': dict(utils.cut(f, '=', ','))})

    for s in segment:
        query = ga.query.refine(query, {'segment': dict(utils.cut(s, '=', ','))})

    return [query]


# TODO: maybe include an --interactive option, which defers
# to `shell` but with a prefilled query?
@cli.command()
@click.argument('metrics')
@click.option('--dimensions')
@click.option('--start',
    help='Start date in ISO format, e.g. 2016-01-01.')
@click.option('--stop')
@click.option('--days',
    help='Days to count forward from start date, counts backwards when negative.',
    default=0,
    type=int)
@click.option('--limit',
    help='Return only the first <n> or <start>,<n> results.')
@click.option('--sort',
    help='Sort by a metric; prefix with - to sort from high to low.')
@click.option('--debug',
    is_flag=True)
@click.option('--filter',
    multiple=True)
@click.option('--segment',
    multiple=True)
@click.option('--precision',
    type=click.IntRange(0, 2),
    default=1,
    help='Increase or decrease query precision.')
@click.option('-i', '--interval',
    type=click.Choice(['hour', 'day', 'week', 'month', 'year', 'total']),
    default='total',
    help='Return hourly, daily etc. numbers.')
@click.option('-o', '--output',
    type=click.Choice(['csv', 'json', 'ascii']),
    default='ascii',
    help='Output format; human-readable ascii table by default.')
@click.option('--with-metadata',
    is_flag=True)
@click.option('-b', '--blueprint',
    type=click.File('r'))
@click.option('--realtime',
    is_flag=True,
    help='Use the RealTime API instead of the Core API.')
@click.pass_obj
def query(scope, blueprint, debug, output, with_metadata, realtime, **description):
    """
    e.g.

        googleanalytics --identity debrouwere --account debrouwere --webproperty http://debrouwere.org \
            query pageviews \
            --start yesterday --limit -10 --sort -pageviews \
            --dimensions pagepath \
            --debug

    """

    if realtime:
        description['type'] = 'realtime'

    if blueprint:
        queries = from_blueprint(scope, blueprint)
    else:
        if not isinstance(scope, ga.account.Profile):
            raise ValueError("Account and webproperty needed for query.")

        queries = from_args(scope, **description)

    for query in queries:
        if debug:
            click.echo(query.build())

        report = query.serialize(format=output, with_metadata=with_metadata)
        click.echo(report)
