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
from tiddlyweb.model.tiddler import Tiddler
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
        bag = source.get(bag)
        tiddlers = bag.list_tiddlers()
        target.put(bag)
        for tiddler in tiddlers:
            for revision_id in source.list_tiddler_revisions(tiddler):
                tiddler_revision = Tiddler(tiddler.title, tiddler.bag)
                tiddler_revision.revision = revision_id
                tiddler_revision = source.get(tiddler_revision)
                print "putting tiddler %s:%s in bag %s" % (tiddler_revision.title, tiddler_revision.revision, tiddler_revision.bag)
                target.put(tiddler_revision)


def init(config_in):
    global config
    config = config_in
