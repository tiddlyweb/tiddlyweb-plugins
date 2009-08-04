
from tiddlyweb.stores import StorageInterface
from tiddlyweb.store import NoBagError, NoRecipeError, NoTiddlerError

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe

BAGS = {}
RECIPES = {}

class Store(StorageInterface):

    def list_recipes(self):
        return [Recipe(recipe) for recipe in sorted(RECIPES.keys())]

    def recipe_put(self, recipe):
        RECIPES[recipe.name] = recipe

    def recipe_get(self, recipe):
        try:
            return RECIPES[recipe.name]
        except KeyError:
            raise NoRecipeError

    def list_bags(self):
        return [Bag(bag) for bag in sorted(BAGS.keys())]

    def bag_put(self, bag):
        BAGS[bag.name] = bag

    def bag_get(self, bag):
        try:
            return BAGS[bag.name]
        except KeyError:
            raise NoBagError

