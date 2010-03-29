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

Here's an example that will migrate from the sql store
to the text store, with the data stored in a dir in
/tmp:

config = {
    'twanager_plugins': ['tiddlywebplugins.migrate'],
    'server_store': ['sql', {'db_config': 'sqlite:///test.db'}],
    'target_store': ['text', {'store_root': '/tmp/backupstore'}],
}

Once the configuration is set the twanager command is run:

    twanager migrate

If the store is large this may take some time.

When tiddlers are migrated from one store to another, they
are stored as new revisions, so if the target store already
exists and has a tiddler of the same name in the same bag,
it will create a new one, extending the revisions.
"""

import copy

from tiddlyweb.manage import make_command
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag
from tiddlyweb.store import Store

@make_command()
def migrate(args):
    """Migrate the content in current store to one described in target_store in config."""
    source_environ = {'tiddlyweb.config': config}
    target_environ = copy.deepcopy(source_environ)
    target_environ['tiddlyweb.config']['server_store'] = config['target_store']
    source_store = Store(config['server_store'][0], config['server_store'][1], source_environ)
    target_store = Store(config['target_store'][0], config['target_store'][1], target_environ)

    if args:
        migrate_bags(source_store, target_store, bags=args)
    else:
        migrate_users(source_store, target_store)
        migrate_recipes(source_store, target_store)
        migrate_bags(source_store, target_store)


def migrate_recipes(source, target):
    print "migrate recipes"
    for recipe in source.list_recipes():
        recipe = source.get(recipe)
        print "putting recipe %s" % recipe.name.encode('utf-8')
        target.put(recipe)


def migrate_users(source, target):
    print "migrate users"
    for user in source.list_users():
        user = source.get(user)
        print "putting user %s" % user.usersign.encode('utf-8')
        target.put(user)


def migrate_bags(source, target, bags=None):
    print "migrate bags"
    if bags:
        bags = [Bag(bag) for bag in bags]
    else:
        bags = source.list_bags()

    for bag in bags:
        bag = source.get(bag)
        tiddlers = bag.list_tiddlers()
        target.put(bag)
        for tiddler in tiddlers:
            for revision_id in reversed(source.list_tiddler_revisions(tiddler)):
                tiddler_revision = Tiddler(tiddler.title, tiddler.bag)
                tiddler_revision.revision = revision_id
                tiddler_revision = source.get(tiddler_revision)
                print "putting tiddler %s:%s in bag %s" % (tiddler_revision.title.encode('utf-8'), tiddler_revision.revision, tiddler_revision.bag.encode('utf-8'))
                tiddler_revision.revision = None
                target.put(tiddler_revision)


def init(config_in):
    global config
    config = config_in
