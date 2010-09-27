"""
A TiddlyWeb plugin which adds a _hash field to a tiddler in two ways.

* When a tiddler is put to the store one or more of its attributes is
  digested to a hash which is then saved with the tiddler.

* When a tiddler is get from the store, if there is no _hash, then the
  hash is added to the outgoing tiddler. It is _not_ saved

This is done to allow quick comparisons between tiddlers which may have
different names but may have the same set of content characteristics.

By default the attribute from which the digest is created is 'text'.

Copyright 2010, Chris Dent <cdent@peermore.com>
Licensed under the same terms as TiddlyWeb.

To use add 'tiddlywebplugins.hashmaker' to system_plugins and
twanager_plugins in tiddlywebconfig.py. Optionally define 
hashmaker.attributes to be a list of strings representing the attributes
or fields of a tiddler which are to be hashed. The default is:

    ['text']
"""
__version__ = '0.2'


from tiddlyweb.store import HOOKS
from tiddlyweb.util import sha


def hash_tiddler_hook(storage, tiddler):
    """
    Wrap hash_tiddler in the hook signature.
    """
    hash_tiddler(storage.environ, tiddler)


def hash_tiddler(environ, tiddler):
    """
    Given tiddler, add a _hash field which is a digest of the
    attributes named in config['hashmaker.attributes'].
    """
    if '_hash' not in tiddler.fields:
        config = environ['tiddlyweb.config']
        attributes= config.get('hashmaker.attributes', ['text'])
        hash = sha()
        for attribute in attributes:
            try:
                data = getattr(tiddler, attribute)
            except AttributeError:
                data = tiddler.fields.get(attribute, '')
            try:
                hash.update(data.encode('utf-8'))
            except (UnicodeEncodeError, UnicodeDecodeError):
                hash.update(data)
        tiddler.fields['_hash'] = hash.hexdigest()


def init(config):
    """
    Establish the hook and validator.
    """
    HOOKS['tiddler']['get'].append(hash_tiddler_hook)
