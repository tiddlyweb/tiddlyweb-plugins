"""
A simple logout plugin that works with the simple_cookie
extractor.
"""

import Cookie
import time


def logout(environ, start_response):
    """
    Break the web by allowing a logout on a GET request.
    And then break it further by sending a bad redirect.
    """
    uri = environ.get('HTTP_REFERER',
            environ['tiddlyweb.config'].get('logout_uri', '/'))
    path = environ.get('tiddlyweb.config', {}).get('server_prefix', '')
    cookie = Cookie.SimpleCookie()
    cookie['tiddlyweb_user'] = ''
    cookie['tiddlyweb_user']['path'] = '%s/' % path
    cookie['tiddlyweb_user']['max-age'] = '0'
    start_response('303 See Other', [
        ('Set-Cookie', cookie.output(header='')),
        ('Location', uri)
        ])
    return [uri]


def init(config):
    config['selector'].add('/logout', GET=logout)
