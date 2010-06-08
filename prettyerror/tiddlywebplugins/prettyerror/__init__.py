"""
Pretty Errors for TiddlyWeb
"""

__version__ = '0.6'

from tiddlyweb.web.http import HTTPExceptor, HTTP404
from tiddlywebplugins.prettyerror.exceptor import PrettyHTTPExceptor
import selector

def replacement_not_found(klass, environ, start_response):
    raise HTTP404('path not found')

selector.Selector.status404 = replacement_not_found


def init(config):
    if PrettyHTTPExceptor not in config['server_response_filters']:
        config['server_response_filters'].insert(
                config['server_response_filters'].index(HTTPExceptor) + 1,
                PrettyHTTPExceptor)
        config['server_response_filters'].remove(HTTPExceptor)
