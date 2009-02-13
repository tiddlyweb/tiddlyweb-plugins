"""
A quick plugin that allows migrating entities from one 
tiddlyweb data store to another. It works by having two
Store instances, one using the source configuration and
and another using the target configuration. Each container
entity is enumerated and then put to the new store.

To use add a 'target_store' key to the _source_
tiddlywebconfig.py and run 'twanager migrate'. 

'target_store' has the same exact format as 'server_store'.
See tiddlyweb.config for more details.
"""

import copy

from tiddlyweb.manage import make_command
from tiddlyweb.store import Store

@make_command()
def migrate(args):
    """Migrate the content in current store to one described in target_store in config."""
    source_environ = {'tiddlyweb.config': config}
    target_environ = copy.deepcopy(source_environ)
    target_environ['tiddlyweb.config']['server_store'] = config['target_store']
    source_store = Store(config['server_store'][0], source_environ)
    target_store = Store(config['target_store'][0], target_environ)

    migrate_users(source_store, target_store)
    migrate_recipes(source_store, target_store)
    migrate_bags(source_store, target_store)


def migrate_recipes(source, target):
    print "migrate recipes"
    for recipe in source.list_recipes():
        print "putting recipe %s" % recipe.name
        target.put(recipe)


def migrate_users(source, target):
    print "migrate users"
    for user in source.list_users():
        print "putting user %s" % user.usersign
        target.put(user)


def migrate_bags(source, target):
    print "migrate bags"
    for bag in source.list_bags():
        source.get(bag)
        tiddlers = bag.list_tiddlers()
        target.put(bag)
        for tiddler in tiddlers:
            for revision in source.list_tiddler_revisions(tiddler):
                tiddler.revision = revision
                source.get(tiddler)
                print "putting tiddler %s in bag %s" % (tiddler.title, tiddler.bag)
                target.put(tiddler)


def init(config_in):
    global config
    config = config_in
