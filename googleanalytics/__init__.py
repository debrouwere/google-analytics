# encoding: utf-8

import pkg_resources

from . import auth, commands, tests, utils, account, auth, blueprint, columns, errors, query, segments
from .auth import authenticate, authorize, revoke
from .blueprint import Blueprint

__version__ = pkg_resources.get_distribution("googleanalytics").version