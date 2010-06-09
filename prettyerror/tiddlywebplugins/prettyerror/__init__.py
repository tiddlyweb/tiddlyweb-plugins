"""
Pretty Errors for TiddlyWeb

This module initializes the plugin.

See tiddlywebplugins.prettyerror.exceptor for details
on operation.
"""

__version__ = '0.7'


import selector

from tiddlyweb.web.http import HTTPExceptor, HTTP404
from tiddlywebplugins.prettyerror.exceptor import PrettyHTTPExceptor


def replacement_not_found(klass, environ, start_response):
    """
    Replaces the selector not_found method with a TiddlyWeb
    exception, so PrettyHTTPExceptor will be engaged when
    selector has no route.
    """
    raise HTTP404('path not found')


selector.Selector.status404 = replacement_not_found


def init(config):
    """
    In server_response_filters replace HTTPExceptor with
    PrettyHTTPExceptor.
    """
    if PrettyHTTPExceptor not in config['server_response_filters']:
        config['server_response_filters'].insert(
                config['server_response_filters'].index(HTTPExceptor) + 1,
                PrettyHTTPExceptor)
        config['server_response_filters'].remove(HTTPExceptor)
