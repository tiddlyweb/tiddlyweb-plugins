"""
A ramstore.

As in, a store which stores stuff in RAM.

Obviously not a great solution if you want persistence,
but good if you want to do some debugging, profiling, or
have some need for a bag or do that is fast and you have
ways to control its persistence and shareability.
"""

from tiddlyweb.stores import StorageInterface
from tiddlyweb.store import NoBagError, NoRecipeError, NoTiddlerError, NoUserError

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.user import User

BAGS = {}
RECIPES = {}
USERS = {}

class Store(StorageInterface):

    def list_users(self):
        return [User(user) for user in sorted(USERS.keys())]

    def user_delete(self, user):
        try:
            del USERS[user.usersign]
        except KeyError:
            raise NoUserError

    def user_put(self, user):
        USERS[user.usersign] = user

    def user_get(self, user):
        try:
            return USERS[user.usersign]
        except KeyError:
            raise NoUserError

    def list_recipes(self):
        return [Recipe(recipe) for recipe in sorted(RECIPES.keys())]

    def recipe_delete(self, recipe):
        try:
            del RECIPES[recipe.name]
        except KeyError:
            raise NoRecipeError

    def recipe_put(self, recipe):
        RECIPES[recipe.name] = recipe

    def recipe_get(self, recipe):
        try:
            return RECIPES[recipe.name]
        except KeyError:
            raise NoRecipeError

    def list_bags(self):
        return [Bag(bag) for bag in sorted(BAGS.keys())]

    def bag_delete(self, bag):
        try:
            del BAGS[bag.name]
        except KeyError:
            raise NoBagError

    def bag_put(self, bag):
        bag.tiddlers = []
        try:
            bag_pair = BAGS[bag.name]
            bag_pair = (bag, bag_pair[1])
        except KeyError:
            bag_pair = (bag, {})
        BAGS[bag.name] = bag_pair

    def bag_get(self, bag):
        try:
            bag_pair = BAGS[bag.name]
        except KeyError:
            raise NoBagError
        bag = bag_pair[0]
        bag.tiddlers = []
        for tiddler_name in bag_pair[1].keys():
            tiddler = bag_pair[1][tiddler_name][-1]
            bag.add_tiddler(tiddler)
        return bag

    def list_tiddler_revisions(self, tiddler):
        bag_name = tiddler.bag
        try:
            bag_pair = BAGS[bag_name]
        except KeyError:
            raise NoBagError
        tiddlers_in_bag = bag_pair[1]
        try:
            tiddler_revisions = tiddlers_in_bag[tiddler.title]
            revisions = [index + 1 for index, tid in enumerate(tiddler_revisions)]
            revisions.reverse()
            return revisions
        except KeyError:
            raise NoTiddlerError

    def tiddler_delete(self, tiddler):
        bag_name = tiddler.bag
        try:
            del BAGS[bag_name][1][tiddler.title]
        except KeyError:
            raise NoTiddlerError


    def tiddler_put(self, tiddler):
        bag_name = tiddler.bag
        try:
            bag_pair = BAGS[bag_name]
        except KeyError:
            raise NoBagError
        tiddlers = bag_pair[1]
        try:
            tiddlers[tiddler.title].append(tiddler)
        except KeyError:
            tiddlers[tiddler.title] = [tiddler]
        # XXX fairly certain needing to set this represents
        # a bug throughout the system.
        tiddler.revision = len(tiddlers[tiddler.title])

    def tiddler_get(self, tiddler):
        bag_name = tiddler.bag
        try:
            bag_pair = BAGS[bag_name]
        except KeyError:
            raise NoBagError
        tiddlers = bag_pair[1]
        try:
            if tiddler.revision:
                revision = tiddler.revision
                tiddler = tiddlers[tiddler.title][tiddler.revision - 1]
                tiddler.revision = revision
            else:
                tiddler = tiddlers[tiddler.title][-1]
                tiddler.revision = len(tiddlers[tiddler.title])
        except (KeyError, IndexError):
            raise NoTiddlerError
        tiddler.created = tiddlers[tiddler.title][0].modified
        for field in tiddler.fields.keys():
            if field.startswith('server.'):
                del tiddler.fields[field]
        return tiddler

    def search(self, query):
        results = []
        for bag_name, bag_pair in BAGS.items():
            bag, tiddlers = bag_pair
            if tiddlers:
                for tiddler_revisions in tiddlers.values():
                    tiddler = tiddler_revisions[-1]
                    if query in tiddler.title:
                        results.append(Tiddler(tiddler.title, bag_name))
                        continue
                    if tiddler.text and query in tiddler.text:
                        results.append(Tiddler(tiddler.title, bag_name))
        return results
