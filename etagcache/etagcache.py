"""
A plugin that provides middleware which keeps an
up to date cache of the ETags produced for
various URLs.

If an incoming GET request has an If-None-Match header,
then the current REQUEST_URI is looked up in the cache.
If the If-None-Match and the value (if any) in the cache
are the same, an HTTP 304 is immediately returned and
internal processing is not done.

As the response is being processed, if the outgoing
response (to a GET request) has an ETag, then that
ETag is returned to the cache as the value for the key
of REQUEST_URI.

tiddler_written, from the store, is hooked to delete
entries in the cache related to that tiddler, determining
what these entries should be is difficult when considering
recipes so for the time being only bag based URIs are cached.
"""

import logging

from tiddlyweb.web.negotiate import Negotiate
from tiddlyweb.web.http import HTTP304
from tiddlyweb.web.util import tiddler_url, get_serialize_type

from tiddlyweb.stores import StorageInterface

import memcache
ETAGS = None

class EtagCache(object):

    def __init__(self, application):
        self.application = application

    def _canonical_url(self, environ):
        url = environ['REQUEST_URI'] or environ['PATH_INFO']
        server_prefix = environ['tiddlyweb.config']['server_prefix']
        if server_prefix and server_prefix in url:
            url = url.replace(server_prefix, '', 1)
        extensions = environ['tiddlyweb.config'].get('extension_types', {}).keys()
        try:
            shorter_url, url_extension = url.rsplit('.', 1)
            if url_extension in extensions:
                url = shorter_url
        except ValueError:
            pass
        logging.debug('calculated url: %s' % url)
        return url

    def __call__(self, environ, start_response):

        def etag_start_response(status, headers, exc_info=None):
            self.status = status
            self.headers = headers

        url = self._canonical_url(environ)

        if environ['REQUEST_METHOD'] == 'GET':
            # will raise 304 if there is a match
            self._check_etag(environ, url)

        output = self.application(environ, etag_start_response)

        if '/bags/' in url:
            try:
                found_etag = [value for header, value in self.headers if header.lower() == 'etag'][0]
                content_type = [value for header, value in self.headers if header.lower() == 'content-type'][0]
                content_type = content_type.split(';', 1)[0]
                username = environ['tiddlyweb.usersign']['name']
            except IndexError:
                found_etag = None

            if found_etag:
                key = '%s:%s:%s' % (url, content_type, username)
                logging.debug('setting cache with %s for %s' % (found_etag, key))
                ETAGS.set(str(key), found_etag)

        start_response(self.status, self.headers)
        return output

    def _check_etag(self, environ, url):
        if '/bags/' in url:
            try:
                etag = environ['HTTP_IF_NONE_MATCH']
                content_type = get_serialize_type(environ)[1]
                content_type = content_type.split(';', 1)[0]
                username = environ['tiddlyweb.usersign']['name']
                key = '%s:%s:%s' % (url, content_type, username)
                found_etag = ETAGS.get(str(key))
                logging.debug('checking etag: %s:%s:%s' % (etag, key, found_etag))
                if etag == found_etag:
                    logging.debug('etag match in cache: %s:%s' % (etag, key))
                    raise HTTP304(found_etag)
            except KeyError:
                pass # no etag just carry on with normal processing
        return # etags didn't match we carry on

def _tiddler_written_handler(self, tiddler):
    bag_name = tiddler.bag
    recipe_name = tiddler.recipe
    # There's no good way to review each key in the cache, so
    # if we do a write, just flush everything!
    global ETAGS
    if not ETAGS:
        try:
            config = self.environ['tiddlyweb.config']
        except KeyError:
            from tiddlyweb.config import config
        ETAGS = memcache.Client(config['memcache_hosts'])
    ETAGS.flush_all()

StorageInterface.tiddler_written = _tiddler_written_handler

def init(config):
    # XXX we need to only add to filters if we are over web
    if config['selector']:
        config['server_request_filters'].insert(
                config['server_request_filters'].index(Negotiate) + 1, EtagCache)
    global ETAGS
    ETAGS = memcache.Client(config['memcache_hosts'])
