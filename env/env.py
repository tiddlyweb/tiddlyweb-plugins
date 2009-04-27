"""
Simple plugin to display the environment.

Mainly useful for exploration or debugging.
"""

from pprint import pformat


def env(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return [pformat(environ)]


def init(config):
    config['selector'].add('/env', GET=env)
    config['selector'].add('/env/{stuff:any}', GET=env)
