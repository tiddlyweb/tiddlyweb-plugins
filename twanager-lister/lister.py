"""
An example of a manager_plugin.

By importing make_command() we are able
to add commands to the command line manager
tool.

This example adds commands for listing
bags, recipes and tiddlers.
"""

from tiddlyweb.manage import make_command
from tiddlyweb.store import Store
from tiddlyweb.serializer import Serializer

def _store():
    return Store(config['server_store'][0], environ={'tiddlyweb.config': config})

@make_command()
def lusers(args):
    """List all the users on the system"""
    store = _store()
    users = store.list_users()
    for user in users:
        user = store.get(user)
        print user.usersign, user.list_roles()


@make_command()
def lbags(args):
    """List all the bags on the system"""
    store = _store()
    bags = store.list_bags()
    serializer = Serializer('json')
    for bag in bags:
        bag = store.get(bag)
        serializer.object = bag
        print 'Name: %s' % bag.name
        print serializer.to_string()
        print


@make_command()
def lrecipes(args):
    """List all the recipes on the system"""
    store = _store()
    recipes = store.list_recipes()
    for recipe in recipes:
        recipe = store.get(recipe)
        print recipe.name, recipe.policy.owner


@make_command()
def ltiddlers(args):
    """List all the tiddlers on the system"""
    store = _store()
    bags = store.list_bags()
    for bag in bags:
        bag = store.get(bag)
        print bag.name, bag.policy.owner
        tiddlers = bag.list_tiddlers()
        for tiddler in tiddlers:
            tiddler = store.get(tiddler)
            print '  ', tiddler.title, tiddler.modifier


def init(config_in):
    global config
    config = config_in
