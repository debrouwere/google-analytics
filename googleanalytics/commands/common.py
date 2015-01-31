# encoding: utf-8

import click
import inspector

import googleanalytics as ga


@click.group()
def cli():
    pass

def authenticated(fn):
    @inspector.wraps(fn)
    @click.option('--identity')
    def authenticated_fn(identity=None, *vargs, **kwargs):
        accounts = ga.authenticate(identity=identity, interactive=True, save=True)
        return fn(identity, accounts, *vargs, **kwargs)
    return authenticated_fn
