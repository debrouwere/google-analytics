# encoding: utf-8

import click
import inspector

import googleanalytics as ga


@click.group(invoke_without_command=True)
@click.option('--identity')
@click.option('--account')
@click.option('--webproperty')
@click.option('--profile')
@click.option('--version', is_flag=True)
@click.pass_context
def cli(ctx, identity, account, webproperty, profile, version):
    ctx.obj = ga.authenticate(
        identity=identity,
        account=account,
        webproperty=webproperty,
        profile=profile,
        interactive=True,
        save=True)

    if version:
        click.echo('googleanalytics {}'.format(ga.__version__))