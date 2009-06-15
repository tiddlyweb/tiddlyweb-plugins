"""
A plugin which listens at '/'
and effectively redirects (by code not HTTP) to 
specified tiddlywiki generating recipes depending
on whether the current user has a particular role.

When possible a cache of the generated wikis will 
be maintained. The cache is used at two level:
if the incoming request has an If-None-Match header
the etag will be validated. If valid, a 304 response
will be sent. Otherwise the a static file will be
read off the disk. If there is no file on the disk,
the storage system will produce the required data.

When a tiddler is written to the store, the cache
is erased.

Originally developed to host http://www.osmosoft.com/

To use, set the constants below. These will 
eventually work through tiddlywebconfig.py.

"""


import logging
import os

from tiddlywebplugins import replace_handler
from tiddlyweb.web.handler.recipe import get_tiddlers
from tiddlyweb.web.http import HTTP304


import tiddlyweb.stores.text

DEFAULT_RECIPE = 'docs'
EDITOR_RECIPE = 'editor'
EDITOR_ROLE = 'ADMIN'
WIKI_CACHE_DIR = '.wiki_cache'


def tiddler_written_handler(self, tiddler):
    try:
        logging.debug('attempting to unlink cache')
        [os.unlink(os.path.join(WIKI_CACHE_DIR, file)) for file in
                os.listdir(WIKI_CACHE_DIR) if not file.startswith('.')]
    except (IOError, OSError), exc:
        logging.warn('unable to unlink in %s: %s' % (WIKI_CACHE_DIR, exc))

# XXX: note this is a dependency on the text store, which is _bad_
tiddlyweb.stores.text.Store.tiddler_written = tiddler_written_handler


def home(environ, start_response):
    """
    If we have a user with role EDITOR_ROLE,
    go one place, otherwise go another,
    by way of recipe injection.
    """
    recipe_name = DEFAULT_RECIPE
    if EDITOR_ROLE in environ['tiddlyweb.usersign'].get('roles', []):
        recipe_name = EDITOR_RECIPE

    if_none_match = environ.get('HTTP_IF_NONE_MATCH', None)
    saved_headers = {}
    def our_start_response(status, headers, exc_info=None):
        etag = _header_value(headers, 'etag')
        saved_headers['etag'] = etag
        logging.debug('response has etag of %s' % etag)
        start_response(status, headers)

    try:
        _validate_cache(if_none_match, recipe_name)
        output, out_etag = _read_cache(recipe_name)
        start_response('200 OK', [
            ('Content-Type', 'text/html; charset=UTF-8'),
            ('Etag', out_etag),
            ])
    except (IOError, OSError), exc:
        logging.debug('cache miss for %s: %s' % (recipe_name, exc))
        environ['wsgiorg.routing_args'][1]['recipe_name'] = recipe_name
        environ['tiddlyweb.type'] = 'text/x-tiddlywiki'
        output = get_tiddlers(environ, our_start_response)
        _write_cache(recipe_name, saved_headers.get('etag', None), output)
    return output


def _validate_cache(etag, name):
    if not etag:
        return
    path = os.path.join(WIKI_CACHE_DIR, etag)
    link_filename = os.path.join(WIKI_CACHE_DIR, name)
    linked_etag = os.path.basename(os.path.realpath(link_filename))
    logging.debug('attempting to validate %s' % path)
    if etag == linked_etag and os.path.exists(path):
        logging.debug('validated %s' % etag)
        raise HTTP304(etag)
    

def _read_cache(name):
    logging.debug('attempt to read %s from cache' % name)
    path = os.path.join(WIKI_CACHE_DIR, name)
    real_path = os.path.basename(os.path.realpath(path))
    return open(os.path.join(WIKI_CACHE_DIR, name)).readlines(), real_path


def _write_cache(name, etag, output):
    etag_filename = os.path.join(WIKI_CACHE_DIR, etag)
    link_filename = os.path.join(WIKI_CACHE_DIR, name)
    file = open(etag_filename, 'w')
    content = ''.join(output)
    file.write(content.encode('UTF-8'))
    file.close()
    logging.debug('attempt to write %s to cache' % name)
    destination_filename = os.path.abspath(link_filename)
    try:
        if os.path.exists(destination_filename):
            os.unlink(destination_filename)
        os.symlink(os.path.abspath(etag_filename), destination_filename)
    except (IOError, OSError), exc:
        logging.warn('unable to link %s <- %s: %s' % (etag_filename, link_filename, exc))



def init(config):
    try:
        os.mkdir(WIKI_CACHE_DIR)
    except (IOError, OSError), exc:
        logging.warn('unable to create %s: %s' % (WIKI_CACHE_DIR, exc))
    replace_handler(config['selector'], '/', dict(GET=home))


def _header_value(headers, name):
    name = name.lower()
    try:
        found_value = [value for header,value in headers if header.lower() == name][0]
    except IndexError:
        found_value = None
    return found_value

