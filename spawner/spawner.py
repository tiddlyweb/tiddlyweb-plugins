"""
A factory for use with spawning so TiddlyWeb can 
run under that high performance, non-blocking web
server.

Use like so:

    spawn --factory=spawner.factory ''

(The empty string argument is necessary for the time being).

spawning can be found on pypi:

    http://pypi.python.org/pypi/Spawning
"""

import tiddlyweb.web.serve
from tiddlyweb.config import config


def factory(args):
    args['app_factory'] = 'spawner.app_factory'
    return args


def app_factory(args):
    return tiddlyweb.web.serve.load_app(prefix=config['server_prefix'])
