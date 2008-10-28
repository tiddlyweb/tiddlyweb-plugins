"""
A StorageInterface that uses a simplified directory
structure compared to the default text store. 

Bugs:

    * description and policy need to have their
      names changed so that we can have tiddlers
      with name description and policy.
"""

import os
import os.path

from  tiddlyweb.stores.text import Store as Text, _encode_filename

class Store(Text):

    def __init__(self, environ={}):
        self.environ = environ
        if not os.path.exists(self._store_root()):
            os.mkdir(self._store_root())

    def _recipe_path(self, recipe):
        return os.path.join(self._store_root(), _encode_filename(recipe.name) + '.recipe')

    def _bag_path(self, bag_name):
        try:
            return os.path.join(self._store_root(), _encode_filename(bag_name))
        except (AttributeError, StoreEncodingError), exc:
            raise NoBagError('No bag name: %s' % exc)

    def _tiddlers_dir(self, bag_name):
        return self._bag_path(bag_name)

    def _files_in_dir(self, path):
        return [x for x in os.listdir(path) if not x.startswith('.') and not x == 'policy' and not x == 'description']
