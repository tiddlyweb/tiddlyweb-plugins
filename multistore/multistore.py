"""
A storage implementation for TiddlyWeb that can read and write
to and from multiple other storage implementations.

That is every time a read or a write operation is done through multistore,
that operation is called on the other configured implementations, so, for
example, when a tiddler is written, it can be written to multiple places.

This is for the entire data store. Other plugins which make different
storage decisions based what bag is being read or written to are being
explored.

There can be as many readers and writers as desired.

If there are multiple readers, all readers are read, but the content
returned comes from the last reader. You probably want just one
reader, but if you want to use multiples for some reason, the power
is there.
"""
import copy

from tiddlyweb.store import Store as Storer
from tiddlyweb.stores import StorageInterface

class Store(StorageInterface):

    def __init__(self, store_config=None, environ=None):
        super(Store, self).__init__(store_config, environ)
        self.readers = []
        self.writers = []
        self._init_store()

    def _init_store(self):
        server_store = self.environ['tiddlyweb.config']['server_store']
        store_config = server_store[1]
        readers = store_config['readers']
        writers = store_config['writers']

        for reader in readers:
            self.readers.append(Storer(reader[0], reader[1], self.environ))
        for writer in writers:
            self.writers.append(Storer(writer[0], reader[1], self.environ))

    def _delete(self, entity):
        for writer in self.writers:
            writer.delete(entity)

    def _get(self, entity):
        for reader in self.readers:
            entity = reader.get(entity)
        return entity

    def _put(self, entity):
        for writer in self.writers:
            writer.put(entity)

    def recipe_delete(self, recipe):
        self._delete(recipe)

    def recipe_get(self, recipe):
        return self._get(recipe)

    def recipe_put(self, recipe):
        self._put(recipe)

    def bag_delete(self, bag):
        self._delete(bag)

    def bag_get(self, bag):
        return self._get(bag)

    def bag_put(self, bag):
        self._put(bag)

    def tiddler_delete(self, tiddler):
        self._delete(tiddler)

    def tiddler_get(self, tiddler):
        return self._get(tiddler)

    def tiddler_put(self, tiddler):
        self._put(tiddler)

    def user_delete(self, user):
        self._delete(user)

    def user_get(self, user):
        return self._get(user)

    def user_put(self, user):
        self._put(user)

    def list_recipes(self):
        for reader in self.readers:
            recipes = reader.list_recipes()
        return recipes

    def list_bags(self):
        for reader in self.readers:
            bags = reader.list_bags()
        return bags

    def list_users(self):
        for reader in self.readers:
            users = reader.list_users()
        return users

    def list_tiddler_revisions(self, tiddler):
        for reader in self.readers:
            revisions = reader.list_tiddler_revisions(tiddler)
        return revisions

    def search(self, search_query):
        for reader in self.readers:
            tiddlers = reader.search(search_query)
        return tiddlers
