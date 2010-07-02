"""
Whoosh based index/search system for TiddlyWeb.

whoosher is a plugin for tiddlyweb. To use, update
tiddlywebconfig.py to include 'tiddlywebplugins.whoosher'
in system_plugins and twanager_plugins:

    config = {
            'twanager_plugins': ['tiddlywebplugins.whoosher'],
            'system_plugins': ['tiddlywebplugins.whoosher'],
    }

Use 'twanager wreindex' to establish an index for an existing
store. For very large stores it is necessary to index in chunks,
do this by providing an optional prefix. If the tiddlers to be
indexed do not start with prefix, they will not be indexed. For
example 'twanager wreindex a' will index all tiddlers whose
title starts with 'a' (case sensitive!).

Over time the index files will be get lumpy. To optimize them,
you may run 'twanager woptimize'. This will lock the index so it
is best to do while the instance server is off.

By default the index is located in a directory called 'indexdir'
off the main instance directory. This may be changed by setting

        'wsearch.indexdir': 'indexdir',

to an absolute or relative path.

Whoosh uses a schema to describe the structure of the index. whoosher
has a reasonable default for this in its static variable SEARCH_DEFAULTS.
That default does not index fields. If there are tiddlers fields that need
to be indexed for a particular installation or application, wsearch.schema
and wsearch.default_fields can be set. _Read the code_ to understand how
these can be used.
"""
import os

import logging
import time

from whoosh.index import create_in, open_dir, EmptyIndexError
from whoosh.fields import Schema, ID, KEYWORD, TEXT
from whoosh.qparser import MultifieldParser, QueryParser
from whoosh.store import LockError

from tiddlywebplugins.utils import get_store

from tiddlyweb.manage import make_command
from tiddlyweb.store import NoTiddlerError
import tiddlyweb.web.handler.search

from tiddlyweb.model.tiddler import Tiddler

from tiddlyweb.stores import TIDDLER_WRITTEN_HANDLERS

IGNORE_PARAMS = []

SEARCH_DEFAULTS = {
        'wsearch.schema': {'title': TEXT,
            'id': ID(stored=True, unique=True),
            'ftitle': ID,
            'bag': TEXT,
            'fbag': ID,
            'text': TEXT,
            'modified': ID,
            'modifier': ID,
            'created': ID,
            'tags': KEYWORD(scorable=True, lowercase=True),
            'field_1': TEXT,
            'field_2': TEXT},
        'wsearch.indexdir': 'indexdir',
        'wsearch.default_fields': ['text', 'title'],
        }

SEARCHER = None
PARSER = None


def init(config):
    if __name__ not in config.get('beanstalk.listeners', []):
        TIDDLER_WRITTEN_HANDLERS.append(_tiddler_written_handler)

    @make_command()
    def wsearch(args):
        """Search the whoosh index for provided terms."""
        query = ' '.join(args)
        ids = search(config, query)
        for result in ids:
            bag, title = result['id'].split(':', 1)
            print "%s:%s" % (bag, title)

    @make_command()
    def wreindex(args):
        """Rebuild the entire whoosh index."""
        try:
            prefix = args[0]
        except IndexError:
            prefix = None
        store = get_store(config)
        schema = config.get('wsearch.schema',
                SEARCH_DEFAULTS['wsearch.schema'])
        for bag in store.list_bags():
            writer = get_writer(config)
            if writer:
                bag = store.get(bag)
                try:
                    tiddlers = bag.get_tiddlers()
                except AttributeError:
                    tiddlers = store.list_bag_tiddlers(bag)
                for tiddler in tiddlers:
                    if prefix and not tiddler.title.startswith(prefix):
                        continue
                    tiddler = store.get(tiddler)
                    index_tiddler(tiddler, schema, writer)
                writer.commit()
            else:
                logging.debug('unable to get writer (locked) for %s', bag.name)

    @make_command()
    def woptimize(args):
        """Optimize the index by collapsing files."""
        index = get_index(config)
        index.optimize()


def whoosh_search(environ):
    """
    Handle incoming /search?q=<query> and
    return the found tiddlers.
    """
    search_query = query_dict_to_search_string(
            environ['tiddlyweb.query']) or ''
    results = search(environ['tiddlyweb.config'], search_query)
    tiddlers = []
    for result in results:
        bag, title = result['id'].split(':', 1)
        tiddler = Tiddler(title, bag)
        tiddlers.append(tiddler)
    return tiddlers

tiddlyweb.web.handler.search.get_tiddlers = whoosh_search


def index_query(environ, **kwargs):
    """
    Return a generator of tiddlers that match
    the provided arguments.
    """
    logging.debug('entering with %s', environ)
    config = environ['tiddlyweb.config']
    #store = environ['tiddlyweb.store']
    query_parts = []
    for field, value in kwargs.items():
        if field == 'tag':
            field = 'tags'
        query_parts.append('%s:%s' % (field, value))
    query_string = ' '.join(query_parts)

    schema = config.get('wsearch.schema', SEARCH_DEFAULTS['wsearch.schema'])
    searcher = get_searcher(config)
    parser = QueryParser('text', schema=Schema(**schema))
    query = parser.parse(query_string)
    logging.debug('query parsed to %s' % query)
    results = searcher.search(query)

    def tiddler_from_result(result):
        bag, title = result['id'].split(':', 1)
        tiddler = Tiddler(title, bag)
        return tiddler
        #return store.get(tiddler)

    for result in results:
        yield tiddler_from_result(result)
    return


def get_index(config):
    """
    Return the current index object if there is one.
    If not attempt to open the index in wsearch.indexdir.
    If there isn't one in the dir, create one. If there is
    not dir, create the dir.
    """
    index_dir = config.get('wsearch.indexdir',
            SEARCH_DEFAULTS['wsearch.indexdir'])
    if not os.path.isabs(index_dir):
        index_dir = os.path.join(config.get('root_dir', ''), index_dir)
    try:
        index = open_dir(index_dir)
    except (IOError, EmptyIndexError):
        try:
            os.mkdir(index_dir)
        except OSError:
            pass
        schema = config.get('wsearch.schema',
                SEARCH_DEFAULTS['wsearch.schema'])
        index = create_in(index_dir, Schema(**schema))
    return index


def get_writer(config):
    """
    Return a writer based on config insructions.
    """
    writer = None
    attempts = 0
    while writer == None and attempts < 5:
        attempts += 1
        try:
            writer = get_index(config).writer()
        except LockError, exc:
            time.sleep(.1)
    return writer


def get_searcher(config):
    """
    Return a searcher based on config instructions.
    """
    return get_index(config).searcher()


def get_parser(config):
    schema = config.get('wsearch.schema', SEARCH_DEFAULTS['wsearch.schema'])
    default_fields = config.get('wsearch.default_fields',
            SEARCH_DEFAULTS['wsearch.default_fields'])
    return MultifieldParser(default_fields, schema=Schema(**schema))


def query_parse(config, query):
    logging.debug('query to parse: %s' % query)
    parser = get_parser(config)
    return parser.parse(query)


def search(config, query):
    """
    Perform a search, returning a whoosh result
    set.
    """
    searcher = get_searcher(config)
    limit = config.get('wsearch.results_limit', 51)
    query = query_parse(config, unicode(query))
    logging.debug('query parsed to %s' % query)
    return searcher.search(query, limit=limit)


def delete_tiddler(tiddler, writer):
    """
    Delete the named tiddler from the index.
    """
    logging.debug('deleting tiddler: %s' % tiddler.title)
    id = _tiddler_id(tiddler)
    writer.delete_by_term('id', id)


def index_tiddler(tiddler, schema, writer):
    """
    Index the given tiddler with the given schema using
    the provided writer.

    The schema dict is read to find attributes and fields
    on the tiddler.
    """
    logging.debug('indexing tiddler: %s' % tiddler.title)
    data = {}
    for key in schema:
        try:
            try:
                value = getattr(tiddler, key)
            except AttributeError:
                value = tiddler.fields[key]
            try:
                data[key] = unicode(value.lower())
            except AttributeError:
                value = ','.join(value)
                data[key] = unicode(value.lower())
        except (KeyError, TypeError), exc:
            pass
        except UnicodeDecodeError, exc:
            pass
    data['id'] = _tiddler_id(tiddler)
    data['ftitle'] = tiddler.title
    data['fbag'] = tiddler.bag
    writer.update_document(**data)


def _tiddler_id(tiddler):
    return '%s:%s' % (tiddler.bag, tiddler.title)


def _tiddler_written_handler(storage, tiddler):
    schema = storage.environ['tiddlyweb.config'].get('wsearch.schema',
            SEARCH_DEFAULTS['wsearch.schema'])
    writer = get_writer(storage.environ['tiddlyweb.config'])
    if writer:
        try:
            store = storage.environ.get('tiddlyweb.store',
                    get_store(storage.environ['tiddlyweb.config']))
            temp_tiddler = store.get(Tiddler(tiddler.title, tiddler.bag))
            index_tiddler(tiddler, schema, writer)
        except NoTiddlerError:
            delete_tiddler(tiddler, writer)
        writer.commit()
    else:
        logging.debug('unable to get writer (locked) for %s:%s',
                tiddler.bag, tiddler.title)


def query_dict_to_search_string(query_dict):
    terms = []
    while query_dict:
        keys = query_dict.keys()
        key = keys.pop()
        values = query_dict[key]
        del query_dict[key]
        if key in IGNORE_PARAMS:
            continue

        if key == 'q':
            terms.extend([value for value in values])
        else:
            if key.endswith('_field'):
                prefix = key.rsplit('_', 1)[0]
                value_key = '%s_value' % prefix
                key = values[0].lower().replace(' ', '_')
                try:
                    values = query_dict[value_key]
                    del query_dict[value_key]
                except KeyError:
                    values = []
                if not values:
                    continue
            elif key.endswith('_value'):
                prefix = key.rsplit('_', 1)[0]
                field_key = '%s_field' % prefix
                try:
                    key = query_dict[field_key][0].lower().replace(' ', '_')
                    del query_dict[field_key]
                except KeyError:
                    key = ''
                if not key:
                    continue

            if key == 'avid' and not values[0].isdigit():
                continue

            for value in values:
                if ' ' in key or ' ' in value:
                    terms.append('%s:"%s"' % (key.lower(), value.lower()))
                else:
                    terms.append('%s:%s' % (key.lower(), value.lower()))
    return ' '.join(terms)


try:
    from tiddlywebplugins.dispatcher.listener import Listener as BaseListener

    class Listener(BaseListener):

        TUBE = 'index'

        def _act(self, job):
            info = self._unpack(job)
            config = self.config
            schema = config.get('wsearch.schema',
                    SEARCH_DEFAULTS['wsearch.schema'])
            tiddler = Tiddler(info['tiddler'], info['bag'])
            writer = get_writer(config)
            if writer:
                try:
                    store = get_store(config)
                    tiddler = store.get(tiddler)
                    index_tiddler(tiddler, schema, writer)
                except NoTiddlerError:
                    delete_tiddler(tiddler, writer)
                writer.commit()
            else:
                logging.debug('unable to get writer (locked) for %s:%s',
                        tiddler.bag, tiddler.title)


except ImportError:
    pass
