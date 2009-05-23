import simplejson
import tiddlyweb


def status(environ, start_response):
    data = _gather_data(environ)
    output = simplejson.dumps(data)
    start_response('200 OK', [
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
