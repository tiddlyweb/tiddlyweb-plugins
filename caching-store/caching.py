
import logging
import memcache

from tiddlyweb.store import Store as StoreBoss
from tiddlyweb.stores import StorageInterface
from tiddlyweb.model.bag import Bag

from tiddlyweb.config import config

from urllib import quote

MC = memcache.Client(config['memcache_hosts'])

class Store(StorageInterface):

    def __init__(self, environ=None):
        if environ is None:
            environ = {}
        self.environ = environ

        internal_store_environ  = {
                'tiddlyweb.config': {
                    'server_store': config['cached_store'],
                    }
                }
        self.cached_store = StoreBoss(config['cached_store'][0], environ=internal_store_environ)

    def recipe_delete(self, recipe):
        key = _recipe_key(recipe)
        MC.delete(key)
        self.cached_store.delete(recipe)

    def recipe_get(self, recipe):
        key = _recipe_key(recipe)
        cached_recipe = _get(key)
        if cached_recipe:
            recipe = cached_recipe
        else:
            recipe = self.cached_store.get(recipe)
            MC.set(key, recipe)
        return recipe

    def recipe_put(self, recipe):
        key = _recipe_key(recipe)
        self.cached_store.put(recipe)
        MC.delete(key)

    def bag_delete(self, bag):
        key = _bag_key(bag)
        if MC.delete(key):
            MC.delete_multi([_tiddler_key(tiddler) for tiddler in bag.list_tiddlers()])
        self.cached_store.delete(bag)

    def bag_get(self, bag):
        key = _bag_key(bag)
        cached_bag = _get(key)
        if cached_bag:
            bag = cached_bag
        else:
            bag = self.cached_store.get(bag)
            MC.set(key, bag)
        return bag

    def bag_put(self, bag):
        key = _bag_key(bag)
        self.cached_store.put(bag)
        MC.delete(key)

    def tiddler_delete(self, tiddler):
        key = _tiddler_key(tiddler)
        if MC.delete(key):
            MC.delete(_bag_key(Bag(tiddler.bag)))
        self.cached_store.delete(tiddler)

    def tiddler_get(self, tiddler):
        key = _tiddler_key(tiddler)
        if not tiddler.revision or tiddler.revision == 0:
            cached_tiddler = _get(key)
            if cached_tiddler:
                tiddler = cached_tiddler
            else:
                tiddler = self.cached_store.get(tiddler)
                MC.set(key, tiddler)
        else:
            tiddler = self.cached_store.get(tiddler)
        return tiddler

    def tiddler_put(self, tiddler):
        key = _tiddler_key(tiddler)
        self.cached_store.put(tiddler)
        MC.delete(_bag_key(Bag(tiddler.bag)))
        MC.delete(key)

    def user_delete(self, user):
        key = _user_key(user)
        MC.delete(key)
        self.cached_store.delete(user)

    def user_get(self, user):
        key = _user_key(user)
        cached_user = _get(key)
        if cached_user:
            user = cached_user
        else:
            user = self.cached_store.get(user)
            MC.set(key, user)
        return user

    def user_put(self, user):
        key = _user_key(user)
        self.cached_store.put(user)
        MC.delete(key)

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
    key = 'tiddler:%s/%s' % (tiddler.bag, tiddler.title)
    return _mangle(key)

def _user_key(user):
    key = 'user:%s' % user.usersign
    return _mangle(key)

def _bag_key(bag):
    key = 'bag:%s' % bag.name
    return _mangle(key)

def _recipe_key(recipe):
    key = 'recipe:%s' % recipe.name
    return _mangle(key)

def _mangle(key):
    return quote(key.encode('UTF-8'), safe='')

def _get(key):
    object = MC.get(key)
    if object:
        logging.debug('cache hit for %s' % key)
    else:
        logging.debug('cache miss for %s' % key)
    return object
