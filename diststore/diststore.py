import copy

from tiddlyweb.store import Store as Storer
from tiddlyweb.stores import StorageInterface

class Store(StorageInterface):

    def __init__(self, environ=None):
        super(Store, self).__init__(environ)
        self.main_store = None
        self.stores = []
        self._init_store()

    def _init_store(self):
        server_store = self.environ['tiddlyweb.config']['server_store']
        server_store_copy = copy.deepcopy(server_store)
        extra_store_config = server_store[1]['extras']
        main_store_config = server_store[1]['main']

        self.environ['tiddlyweb.config']['server_store'] = main_store_config
        self.main_store = Storer(main_store_config[0], self.environ)

        for rule, store in extra_store_config:
            self.environ['tiddlyweb.config']['server_store'] = store
            self.stores.append((rule, Storer(store[0], self.environ)))
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

    def list_users(self):
        return self.main_store.list_users()

    def list_tiddler_revisions(self, tiddler):
        store = self._determine_store(tiddler.bag)
        return store.list_tiddler_revisions(tiddler)

    def search(self, search_query):
        tiddlers = []
        for rule, store in self.stores:
            tiddlers.extend(store.search(search_query))
        tiddlers.extend(self.main_store.search(search_query))
        return tiddlers

    def _determine_store(self, name):
        for rule, store in self.stores:
            if name.startswith(rule):
                return store
        return self.main_store
