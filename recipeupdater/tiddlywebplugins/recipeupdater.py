"""
A twanager command that updates all the recipes in the store
that match a bag filter combo with one or more replacement
bag filter combos:

twanager recipeupdate '/bags/foobar/tiddlers?select=bang' \
    '/bags/foobar/tiddlers' '/bags/anotherbag/tiddlers?select=bag'

To use, add 'tiddlywebplugins.recipeupdater' to twanager_plugins
in tiddlywebconfig.py
"""


from tiddlyweb.manage import make_command
from tiddlywebplugins.utils import get_store

def init(config):

    @make_command()
    def recipeupdate(args):
        """Update all recipes entry with a different entry. <match bag info> <replacement bag info> [<replacement bag info>]"""
        store = get_store(config)
        match_bag = args.pop(0)
        bag, filter = _text_to_tuple(match_bag)
        replace_bags = args
        for recipe in store.list_recipes():
            recipe = store.get(recipe)
            recipe_list = recipe.get_recipe()
            try:
                index = recipe_list.index([bag, filter])
            except ValueError:
                # not in the recipe carry on
                continue
            recipe_list.pop(index)
            for bag_string in reversed(replace_bags):
                bag, filter = _text_to_tuple(bag_string)
                recipe_list.insert(index, (bag, filter))
            recipe.set_recipe(recipe_list)
            store.put(recipe)


def _text_to_tuple(bag_string):
    try:
        bag_string, filter_string = bag_string.split('?')
    except ValueError:
        bag_string = bag_string
        filter_string = ''
    if not filter_string:
        filter_string = ''
    bag_bits = bag_string.split('/')
    if len(bag_bits) < 4:
        raise ValueError('bag string malformed %s' % bag_string)
    bag = bag_bits[2]
    return bag, filter_string

