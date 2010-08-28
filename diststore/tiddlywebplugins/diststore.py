"""
Distribute storage of bag based entities to different
storage sytems based on rules defined in tiddlywebconfig.py.

The rules are regular expressions which match the name of a bag. When a
tiddler or bag is accessed (for read or write) if the name of the bag
matches a regular expression in the store's "extras" dictionary, the
store named in the value is responsible for the entity being accessed.
Otherwise the store named in "main" is used.

The value of the main key and of each regular expression entry in
the extras takes the same form as the 'server_store' entry: a list
or tuple of two items:

    * The name of the module providing the store.
    * A dictionary with the configuration information the store needs.
"""

__version__ = '0.7' 

import copy
import re

from tiddlyweb.store import Store as Storer, StoreMethodNotImplemented
from tiddlyweb.stores import StorageInterface

class Store(StorageInterface):

    def __init__(self, store_config=None, environ=None):
        super(Store, self).__init__(store_config, environ)
        self.main_store = None
        self.stores = []
        self._init_store()

    def _init_store(self):
        server_store = self.environ['tiddlyweb.config']['server_store']
        server_store_copy = copy.deepcopy(server_store)
        extra_store_config = server_store[1]['extras']
        main_store_config = server_store[1]['main']

        self.environ['tiddlyweb.config']['server_store'] = main_store_config
        self.main_store = Storer(main_store_config[0], main_store_config[1], self.environ)

        for rule, store in extra_store_config:
            pattern = re.compile(rule)
            self.environ['tiddlyweb.config']['server_store'] = store
            self.environ['tiddlyweb.config']['main_store'] = self.main_store
            self.stores.append((pattern, Storer(store[0], store[1], self.environ)))
        self.environ['tiddlyweb.config']['server_store'] = server_store_copy

    def recipe_delete(self, recipe):
        self.main_store.delete(recipe)

    def recipe_get(self, recipe):
        return self.main_store.get(recipe)

    def recipe_put(self, recipe):
        self.main_store.put(recipe)

    def bag_delete(self, bag):
        store = self._determine_store(bag.name)
        store.delete(bag)

    def bag_get(self, bag):
        store = self._determine_store(bag.name)
        return store.get(bag)

    def bag_put(self, bag):
        store = self._determine_store(bag.name)
        store.put(bag)

    def tiddler_delete(self, tiddler):
        store = self._determine_store(tiddler.bag)
        store.delete(tiddler)

    def tiddler_get(self, tiddler):
        store = self._determine_store(tiddler.bag)
        return store.get(tiddler)

    def tiddler_put(self, tiddler):
        store = self._determine_store(tiddler.bag)
        store.put(tiddler)

    def user_delete(self, user):
        self.main_store.delete(user)

    def user_get(self, user):
        return self.main_store.get(user)

    def user_put(self, user):
        return self.main_store.put(user)

    def list_recipes(self):
        return self.main_store.list_recipes()

    def list_bags(self):
        bags = []
        for rule, store in self.stores:
            bags.extend(store.list_bags())
        bags.extend(self.main_store.list_bags())
        return bags

    def list_bag_tiddlers(self, bag):
        store = self._determine_store(bag.name)
        return store.list_bag_tiddlers(bag)

    def list_users(self):
        return self.main_store.list_users()

    def list_tiddler_revisions(self, tiddler):
        store = self._determine_store(tiddler.bag)
        return store.list_tiddler_revisions(tiddler)

    def search(self, search_query):
        tiddlers = []
        searched = False
        for rule, store in self.stores:
            try:
                tiddlers.extend(store.search(search_query))
                searched = True
            except StoreMethodNotImplemented:
                pass # just ride right over those stores that don't search
        try:
            tiddlers.extend(self.main_store.search(search_query))
            searched = True
        except StoreMethodNotImplemented:
            pass
        if not searched:
            raise StoreMethodNotImplemented
        return tiddlers

    def _determine_store(self, name):
        for pattern, store in self.stores:
            # XXX should this be search or match?
            if pattern.match(name):
                return store
        return self.main_store
