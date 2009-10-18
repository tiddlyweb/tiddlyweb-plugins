"""
status is a TiddlyWeb plugins which gives a JSON report on
the current state of the server including:

* current user
* TiddlyWeb version
* available challengers

To use, add 'tiddlywebplugins.status' to 'system_plugins'
in 'tiddlywebconfig.py':

    config = {
        'system_plugins': [
            'tiddlywebplugins.status',
        ]
    }

Once running the plugin will add a route at
'{server_prefix}/status' that reports a JSON data
structure with the information described above.

This is primarily used to determine who is the current
TiddlyWeb user.
"""

__version__ = '0.2'
__author__ = 'Chris Dent (cdent@peermore.com)'
__copyright__ = 'Copyright UnaMesa Association 2008-2009'
__contributors__ = ['Frederik Dohr']
__license__ = 'BSD'


import simplejson
import tiddlyweb


def status(environ, start_response):
    data = _gather_data(environ)
    output = simplejson.dumps(data)
    start_response('200 OK', [
        ('Cache-Control', 'no-cache'),
        ('Content-Type', 'application/json')
        ])
    return [output]


def init(config):
    config['selector'].add('/status', GET=status)


def _gather_data(environ):
    return {
            'username': environ['tiddlyweb.usersign']['name'],
            'version': tiddlyweb.__version__,
            'challengers': environ['tiddlyweb.config']['auth_systems'],
            }
