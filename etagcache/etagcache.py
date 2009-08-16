"""
A plugin that provides middleware which keeps an
update to date cache of the ETags produced for 
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
what these entries should be is niggling.
"""

import logging

from tiddlyweb.web.query import Query
from tiddlyweb.web.http import HTTP304
from tiddlyweb.web.util import tiddler_url

from tiddlyweb.stores import StorageInterface

ETAGS = {}

class EtagCache(object):
    
    def __init__(self, application):
        self.application = application
        
    def _canonical_url(self, environ):
        url = environ['SCRIPT_NAME'] or environ['PATH_INFO']
        server_prefix = environ['tiddlyweb.config']['server_prefix']
        if server_prefix and server_prefix in uri:
            url = uri.replace(server_prefix, '', 1)
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
            except IndexError:
                found_etag = None

            if found_etag:
                logging.debug('setting cache with %s for %s' % (found_etag, url))
                ETAGS[url] = found_etag

        start_response(self.status, self.headers)
        return output

    def _check_etag(self, environ, url):
        if '/bags/' in url:
            try:
                logging.debug('checking for etag')
                etag = environ['HTTP_IF_NONE_MATCH']
                logging.debug('checking etag: %s' % etag)
                found_etag = ETAGS[url]

                if etag == found_etag:
                    logging.debug('etag match in cache: %s' % etag)
                    raise HTTP304(found_etag)
            except KeyError:
                pass # no etag just carry on with normal processing
        return # etags didn't match we carry on

def _tiddler_written_handler(self, tiddler):
    bag_name = tiddler.bag
    recipe_name = tiddler.recipe
    decache_uris = []
    if bag_name:
        tiddler.recipe = None
        single_tiddler_url = tiddler_url(self.environ, tiddler)
        single_tiddler_url = '/' + single_tiddler_url.split('/', 3)[3]
        bag_tiddlers_url = single_tiddler_url.rsplit('/', 1)[0]
        decache_uris.append(single_tiddler_url)
        decache_uris.append(bag_tiddlers_url)
        if recipe_name:
            tiddler.recipe = recipe_name

    server_prefix = self.environ.get('tiddlyweb.config', {}).get('server_prefix', '')
    for uri in decache_uris:
        if server_prefix and server_prefix in uri:
            uri = uri.replace(server_prefix, '', 1)
        try:
            logging.debug('attempting to de-cache: %s' % uri)
            del ETAGS[uri]
            logging.debug('de-cached: %s' % uri)
        except KeyError:
            pass


StorageInterface.tiddler_written = _tiddler_written_handler

def init(config):
    # XXX we need to only add to filters if we are over web
    if config['selector']:
        config['server_request_filters'].insert(
                config['server_request_filters'].index(Query) + 1, EtagCache)
