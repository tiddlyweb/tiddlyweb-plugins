
from lrucache import LRUCache

from cPickle import dumps, loads

from tiddlyweb.store import Store as StoreBoss
from tiddlyweb.stores import StorageInterface

import copy
from pprint import pprint

original_set = LRUCache.__setitem__

def set_with_copy(self, key, obj):
    print "setting key %s" % key
    pickle = dumps(obj)
    return original_set(self, key, pickle)

LRUCache.__setitem__ = set_with_copy

CACHE = LRUCache(10000)


class Store(StorageInterface):

    def __init__(self, environ=None):
        if environ is None:
            environ = {}
        self.environ = environ

        internal_store_config = {
                'tiddlyweb.config': {
                    'server_store': ['text', {'store_root': 'store'}],
                    }
                }
        self.cached_store = StoreBoss('text', environ=internal_store_config)

    def recipe_delete(self, recipe):
        key = _recipe_key(recipe)
        if key in CACHE:
            del CACHE[key]
        self.cached_store.delete(recipe)

    def recipe_get(self, recipe):
        key = _recipe_key(recipe)
        if key in CACHE:
            print 'getting %s' % key
            recipe = loads(CACHE[key])
        else:
            recipe = self.cached_store.get(recipe)
            CACHE[key] = recipe
        return recipe

    def recipe_put(self, recipe):
        key = _recipe_key(recipe)
        self.cached_store.put(recipe)
        CACHE[key] = recipe

    def bag_delete(self, bag):
        key = _bag_key(bag)
        if key in CACHE:
            del CACHE[key]
        self.cached_store.delete(bag)

    def bag_get(self, bag):
        key = _bag_key(bag)
        if key in CACHE:
            print 'getting %s' % key
            bag = loads(CACHE[key])
        else:
            bag = self.cached_store.get(bag)
            CACHE[key] = bag
        return bag

    def bag_put(self, bag):
        key = _bag_key(bag)
        self.cached_store.put(bag)
        CACHE[key] = bag

    def user_delete(self, user):
        key = _user_key(user)
        if key in CACHE:
            del CACHE[key]
        self.cached_store.delete(user)

    def user_get(self, user):
        key = _user_key(user)
        if key in CACHE:
            print 'getting %s' % key
            user = loads(CACHE[key])
        else:
            user = self.cached_store.get(user)
            CACHE[key] = user
        return user

    def user_put(self, user):
        key = _user_key(user)
        self.cached_store.put(user)
        CACHE[key] = user

    def tiddler_delete(self, tiddler):
        key = _tiddler_key(tiddler)
        if key in CACHE:
            del CACHE[key]
        self.cached_store.delete(tiddler)

    def tiddler_get(self, tiddler):
        key = _tiddler_key(tiddler)
        if not tiddler.revision or tiddler.revision == 0 and key in CACHE:
            print 'getting %s' % key
            tiddler = loads(CACHE[key])
        else:
            tiddler = self.cached_store.get(tiddler)
            CACHE[key] = tiddler
        return tiddler

    def tiddler_put(self, tiddler):
        key = _tiddler_key(tiddler)
        self.cached_store.put(tiddler)
        bag_name = tiddler.bag
        del CACHE['bag:' + bag_name]
        CACHE[key] = tiddler

    def list_recipes(self):
        return self.cached_store.list_recipes()

    def list_bags(self):
        return self.cached_store.list_bags()

    def list_users(self):
        return self.cached_store.list_users()

    def list_tiddler_revisions(self, tiddler):
        return self.cached_store.list_tiddler_revisions(tiddler)

    def search(self, search_query):
        return self.cached_store.search(search_query)

def _tiddler_key(tiddler):
    return 'tiddler:%s/%s' % (tiddler.bag, tiddler.title)

def _user_key(user):
    return 'user:%s' % user.name

def _bag_key(bag):
    return 'bag:%s' % bag.name

def _recipe_key(recipe):
    return 'recipe:%s' % recipe.name

