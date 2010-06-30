"""
A simple logout plugin that works with the simple_cookie
extractor.
"""

from tiddlyweb.web.util import server_base_url

import Cookie
import time


def logout(environ, start_response):
    """
    Break the web by allowing a logout on a GET request.
    And then break it further by sending a bad redirect.
    """
    uri = environ.get('HTTP_REFERER',
            server_base_url(environ) +
            environ['tiddlyweb.config'].get('logout_uri', '/'))
    path = environ.get('tiddlyweb.config', {}).get('server_prefix', '')
    cookie = Cookie.SimpleCookie()
    cookie['tiddlyweb_user'] = ''
    cookie['tiddlyweb_user']['path'] = '%s/' % path
    if 'MSIE' in environ.get('HTTP_USER_AGENT', ''):
        cookie['tiddlyweb_user']['expires'] = time.strftime(
                '%a, %d-%m-%y %H:%M:%S GMT', time.gmtime(time.time()-600000))
    else:
        cookie['tiddlyweb_user']['max-age'] = '0'
    cookie_output = cookie.output(header='')
    start_response('303 See Other', [
        ('Set-Cookie', cookie_output),
        ('Expires', time.strftime(
            '%a, %d %b %Y %H:%M:%S GMT', time.gmtime(time.time()-600000))),
        ('Cache-Control', 'no-store'),
        ('Location', uri),
        ])
    return [uri]


def init(config):
    if 'selector' in config:
        config['selector'].add('/logout', GET=logout)
