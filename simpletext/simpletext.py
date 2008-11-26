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
import urllib

from tiddlyweb.stores.text import Store as Text, _encode_filename
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.user import User

class Store(Text):

    def __init__(self, environ={}):
        self.environ = environ
        if not os.path.exists(self._store_root()):
            os.mkdir(self._store_root())

    def list_bags(self):
        bags = self._dirs_in_dir(self._store_root())

        return [Bag(urllib.unquote(bag).decode('utf-8')) for bag in bags]

    def list_recipes(self):
        recipes = [file.replace('.recipe', '') for file in self._files_in_dir(self._store_root()) if file.endswith('.recipe')]

        return [Recipe(urllib.unquote(recipe).decode('utf-8')) for recipe in recipes]

    def list_users(self):
        users = [file.replace('.user', '') for file in self._files_in_dir(self._store_root()) if file.endswith('.user')]

        return [User(urllib.unquote(user).decode('utf-8')) for user in users]

    def _dirs_in_dir(self, path):
        return [dir for dir in self._files_in_dir(path) if os.path.isdir(os.path.join(path, dir))]

    def _recipe_path(self, recipe):
        return os.path.join(self._store_root(), _encode_filename(recipe.name) + '.recipe')

    def _bag_path(self, bag_name):
        try:
            return os.path.join(self._store_root(), _encode_filename(bag_name))
        except (AttributeError, StoreEncodingError), exc:
            raise NoBagError('No bag name: %s' % exc)

    def _user_path(self, user):
        return os.path.join(self._store_root(), user.usersign + '.user')

    def _tiddlers_dir(self, bag_name):
        return self._bag_path(bag_name)

    def _files_in_dir(self, path):
        return [x for x in os.listdir(path) if not x.startswith('.') and not x == 'policy' and not x == 'description']
