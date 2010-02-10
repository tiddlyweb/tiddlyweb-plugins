"""
Override tiddlyweb.web.util:server_host_url to
attend to HTTP_HOST settings.
"""

import tiddlyweb.web.util


original_server_host_url = tiddlyweb.web.util.server_host_url


def virtual_server_host_url(environ):
    http_host = environ.get('HTTP_HOST')
    if http_host:
        return '%s://%s' % (environ['wsgi.url_scheme'], http_host)
    else:
        return original_server_host_url(environ)


tiddlyweb.web.util.server_host_url = virtual_server_host_url


def init(config):
    pass
