# encoding: utf-8

import click
import inspector

import googleanalytics as ga


@click.group()
@click.option('--identity')
@click.option('--account')
@click.option('--webproperty')
@click.option('--profile')
@click.pass_context
def cli(ctx, identity, account, webproperty, profile):
    ctx.obj = ga.authenticate(
        identity=identity,
        account=account,
        webproperty=webproperty,
        profile=profile,
        interactive=True,
        save=True)
