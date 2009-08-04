
from tiddlyweb.stores import StorageInterface
from tiddlyweb.store import NoBagError, NoRecipeError, NoTiddlerError

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe

BAGS = {}
RECIPES = {}

class Store(StorageInterface):

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
        for tiddler_name in bag_pair[1].keys():
            tiddler = bag_pair[1][tiddler_name][-1]
            bag.add_tiddler(tiddler)
        return bag

    def list_tiddler_revisions(self, tiddler):
        bag_name = tiddler.bag
        try:
            bag_pair = BAGS[bag_name]
        except KeyError:
            NoBagError
        tiddlers_in_bag = bag_pair[1]
        try:
            tiddler_revisions = tiddlers_in_bag[tiddler.title]
            return [index + 1 for index, tid in enumerate(tiddler_revisions)]
        except KeyError:
            NoTiddlerError

    def tiddler_delete(self, tiddler):
        bag_name = tiddler.bag
        try:
            del BAGS[bag_name][1][tiddler.title]
        except KeyError:
            NoTiddlerError


    def tiddler_put(self, tiddler):
        bag_name = tiddler.bag
        try:
            bag_pair = BAGS[bag_name]
        except KeyError:
            NoBagError
        tiddlers = bag_pair[1]
        try:
            tiddlers[tiddler.title].append(tiddler)
        except KeyError:
            tiddlers[tiddler.title] = [tiddler]

    def tiddler_get(self, tiddler):
        bag_name = tiddler.bag
        try:
            bag_pair = BAGS[bag_name]
        except KeyError:
            NoBagError
        tiddlers = bag_pair[1]
        try:
            tiddler = tiddlers[tiddler.title][-1]
            tiddler.revision = len(tiddlers[tiddler.title])
        except KeyError:
            raise NoTiddlerError
        return tiddler

    def search(self, query):
        results = []
        for bag_name, bag_pair in BAGS.items():
            bag, tiddlers = bag_pair
            if tiddlers:
                for tiddler_revisions in tiddlers.values():
                    tiddler = tiddler_revisions[-1]
                    if tiddler.text and query in tiddler.text:
                        results.append(tiddler)
        return results

