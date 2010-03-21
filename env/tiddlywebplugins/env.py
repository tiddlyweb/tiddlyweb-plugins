"""
This is a debugging plugin for TiddlyWeb.

When {server_prefix}/env is accessed the current WSGI environment
is returned as text/plain, formatted with pprint.
"""

from pprint import pformat


def env(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return [pformat(environ)]


def init(config):
    config['selector'].add('/env', GET=env)
    config['selector'].add('/env/{stuff:any}', GET=env)
