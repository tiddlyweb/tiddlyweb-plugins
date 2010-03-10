
import logging

from tiddlyweb.store import Store as StoreBoss
from tiddlyweb.stores import StorageInterface
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler

from urllib import quote

class Store(StorageInterface):

    _MC = None

    def __init__(self, store_config=None, environ=None):
        if store_config is None:
            store_config = {}
        if environ is None:
            environ = {}
        self.environ = environ
        self.config = environ.get('tiddlyweb.config')

        self._mc = self._MC

        if self._mc == None:
            try:
                from google.appengine.api import memcache
                self._MC = memcache
            except ImportError:
                import memcache
                try:
                    self._MC = memcache.Client(self.config['memcache_hosts'])
                except KeyError:
                    from tiddlyweb.config import config
                    self.config = config
                    self._MC = memcache.Client(self.config['memcache_hosts'])
            self._mc = self._MC

            self.cached_store = StoreBoss(self.config['cached_store'][0],
                    self.config['cached_store'][1], environ=environ)
            self.prefix = self.config['server_prefix']
            self.host = self.config['server_host']['host']

    def recipe_delete(self, recipe):
        key = self._recipe_key(recipe)
        self._mc.delete(key)
        self.cached_store.delete(recipe)

    def recipe_get(self, recipe):
        key = self._recipe_key(recipe)
        cached_recipe = self._get(key)
        if cached_recipe:
            recipe = cached_recipe
        else:
            recipe = self.cached_store.get(recipe)
            del recipe.store
            self._mc.set(key, recipe)
        return recipe

    def recipe_put(self, recipe):
        key = self._recipe_key(recipe)
        self.cached_store.put(recipe)
        self._mc.delete(key)

    def bag_delete(self, bag):
        key = self._bag_key(bag)
        if self._mc.delete(key):
            tiddlers_in_bag = bag.list_tiddlers()
            for tiddler in tiddlers_in_bag:
                self._mc.delete_multi([self._tiddler_revision_key(
                    self._create_tiddler_revision(tiddler, revision_id)) for
                    revision_id in self.list_tiddler_revisions(tiddler)])
            self._mc.delete_multi([self._tiddler_key(tiddler) for
                tiddler in tiddlers_in_bag])
        self.cached_store.delete(bag)

    def bag_get(self, bag):
        if (hasattr(bag, 'skinny') and bag.skinny):
            key = self._bag_key(bag)
            cached_bag = self._get(key)
            if cached_bag:
                bag = cached_bag
            else:
                bag = self.cached_store.get(bag)
                del bag.store
                self._mc.set(key, bag)
        else:
            bag = self.cached_store.get(bag)
            del bag.store
        return bag

    def bag_put(self, bag):
        key = self._bag_key(bag)
        self.cached_store.put(bag)
        self._mc.delete(key)

    def tiddler_delete(self, tiddler):
        key = self._tiddler_key(tiddler)

        if self._mc.delete(key):
            self._mc.delete(self._bag_key(Bag(tiddler.bag)))
            self._mc.delete_multi([self._tiddler_revision_key(self._create_tiddler_revision(
                tiddler, revision_id)) for revision_id in
                self.list_tiddler_revisions(tiddler)])
        self.cached_store.delete(tiddler)

    def tiddler_get(self, tiddler):
        if not tiddler.revision or tiddler.revision == 0:
            key = self._tiddler_key(tiddler)
        else:
            key = self._tiddler_revision_key(tiddler)
        cached_tiddler = self._get(key)
        if cached_tiddler:
            cached_tiddler.recipe = tiddler.recipe
            tiddler = cached_tiddler
        else:
            tiddler = self.cached_store.get(tiddler)
            del tiddler.store
            self._mc.set(key, tiddler)
        return tiddler

    def tiddler_put(self, tiddler):
        key = self._tiddler_key(tiddler)
        self.cached_store.put(tiddler)
        self._mc.delete(self._bag_key(Bag(tiddler.bag)))
        self._mc.delete(key)

    def user_delete(self, user):
        key = self._user_key(user)
        self._mc.delete(key)
        self.cached_store.delete(user)

    def user_get(self, user):
        key = self._user_key(user)
        cached_user = self._get(key)
        if cached_user:
            user = cached_user
        else:
            user = self.cached_store.get(user)
            del user.store
            self._mc.set(key, user)
        return user

    def user_put(self, user):
        key = self._user_key(user)
        self.cached_store.put(user)
        self._mc.delete(key)

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

    def _create_tiddler_revision(self, tiddler, revision_id):
        revision = Tiddler(tiddler.title, tiddler.bag)
        revision.revision = revision_id
        return revision

    def _tiddler_key(self, tiddler):
        key = 'tiddler:%s/%s' % (tiddler.bag, tiddler.title)
        return self._mangle(key)

    def _tiddler_revision_key(self, tiddler):
        key = 'tiddler:%s/%s/%s' % (tiddler.bag, tiddler.title, tiddler.revision)
        return self._mangle(key)

    def _user_key(self, user):
        key = 'user:%s' % user.usersign
        return self._mangle(key)

    def _bag_key(self, bag):
        key = 'bag:%s' % bag.name
        return self._mangle(key)

    def _recipe_key(self, recipe):
        key = 'recipe:%s' % recipe.name
        return self._mangle(key)

    def _mangle(self, key):
        key = '%s:%s:%s' % (self.host, self.prefix, key)
        return quote(key.encode('UTF-8'), safe='')


    def _get(self, key):
        object = self._mc.get(key)
        if object:
            logging.debug('cache hit for %s' % key)
        else:
            logging.debug('cache miss for %s' % key)
        return object
