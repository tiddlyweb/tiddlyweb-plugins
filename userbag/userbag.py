"""
A store for use with the diststore.

When accessing a bag named 'users', users
that exist in the main store will be presented
as tiddlers. Handling of writes currently undefined.
"""

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import Policy
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.user import User
from tiddlyweb.store import Store as Storer
from tiddlyweb.stores import StorageInterface

DEFAULT_POLICY = {
        'read': ['R:ADMIN'],
        'write': ['R:ADMIN'],
        'create': ['R:ADMIN'],
        'delete': ['R:ADMIN'],
        'accept': ['R:ADMIN'],
        }

class Store(StorageInterface):

    def __init__(self, environ=None):
        super(Store, self).__init__(environ)
        self.main_store = self.environ['tiddlyweb.config']['main_store']

    def list_bags(self):
        # TODO: set policy
        return [Bag('users')]

    def bag_get(self, bag):
        bag.desc = 'Available users'
        bag.policy = self._policy()
        store = self.main_store
        users = store.list_users()
        for user in users:
            tiddler = Tiddler(user.usersign)
            tiddler.bag = bag.name
            bag.add_tiddler(tiddler)
        return bag

    def tiddler_get(self, tiddler):
        store = self.main_store
        username = tiddler.title
        user = User(username)
        user = store.get(user)
        tiddler.text = '%s' % user.list_roles()
        return tiddler

    def _policy(self):
        policy = Policy()
        for key, value in DEFAULT_POLICY.items():
            setattr(policy, key, value)
        return policy
