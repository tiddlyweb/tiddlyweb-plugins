
from tiddlyweb.stores import StorageInterface
from tiddlyweb.store import NoBagError, NoRecipeError, NoTiddlerError

from tiddlyweb.model.bag import Bag

BAGS = {}

class Store(StorageInterface):

    def list_bags(self):
        return [Bag(bag) for bag in sorted(BAGS.keys())]

    def bag_put(self, bag):
        BAGS[bag.name] = bag

    def bag_get(self, bag):
        try:
            return BAGS[bag.name]
        except KeyError:
            raise NoBagError

