"""
A TiddlyWeb plugin for working around limitations
in some server setups wherein perfectly legit 
HTTP methods like PUT and DELETE are not allowed to
pass through to TiddlyWeb.

This can also happen when using some legacy browsers
which will not allow PUT and DELETE in XmlHttpRequest
calls.

We do this by looking at, in order:

    X-HTTP-Method header
    http_method URL parameter

If the real method is POST, REQUEST_METHOD will be
reset to whatever is given in the above.

If the real method is GET, REQUEST_METHOD will only
be reset to whatever is given in the above if it is
GET or HEAD.

Effectively this means that if you want to override,
you must POST. This is consistent with idempotency
conventions associated with HTTP methods.

ONLY USE THIS MIDDLEWARE IF YOU CANNOT FIX YOUR
SERVER OR YOUR BROWSER. YOUR SERVER AND BROWSER ARE
BROKEN IF YOU NEED TO USE THIS.

NOTE: This code will not magically handle tunneling 
of methods. Client code must choose to do the tunneling.
At this time TiddlyWeb client code such as TiddlyWebAdaptor
does NOT tunnel.
"""

import logging

from tiddlyweb.web.query import Query

class MethodHack(object):
    """
    WSGI environment manipulator to override
    the actual HTTP request method with one
    provided in a header.
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        self._munge_request_method(environ)
        return self.application(environ, start_response)

    def _munge_request_method(self, environ):
        header = environ.get('HTTP_X_HTTP_METHOD', None)
        param = environ['tiddlyweb.query'].get('http_method', [None])[0]
        real_method = environ['REQUEST_METHOD']
        tunnel_method = header or param or real_method

        if real_method == 'POST':
            logging.debug('overriding POST method to %s' % tunnel_method)
            environ['REQUEST_METHOD'] = tunnel_method
        elif real_method == 'GET' and (tunnel_method == 'GET' or tunnel_method == 'HEAD'):
            logging.debug('overriding GET method to %s' % tunnel_method)
            environ['REQUEST_METHOD'] = tunnel_method


def init(config):
    config['server_request_filters'].insert(
            config['server_request_filters'].index(Query) + 1, MethodHack)
