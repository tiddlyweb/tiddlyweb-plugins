"""
A bug was discovered wherein revisions were
not being deleted from the cache properly.
This test confirms it is fixed. In the process
it should confirm generally workingness.
"""

from tiddlyweb.config import config
from tiddlyweb.store import Store, NoTiddlerError

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag

import py.test


def setup_module(module):
    module.store = Store(config['server_store'][0], config['server_store'][1],
            environ={'tiddlyweb.config': config})
    try:
        bag = Bag('holder')
        store.delete(bag)
    except:
        pass
    bag = Bag('holder')
    module.store.put(bag)


def test_memcache_up():
    store.storage._mc.set('keyone', 'valueone')
    assert store.storage._mc.get('keyone') == 'valueone'
    store.storage._mc.delete('keyone')


def test_put_get_tiddlers():
    tiddler = Tiddler('tiddler1', 'holder')
    tiddler.text = 'rev1'
    store.put(tiddler)
    tiddler.text = 'rev2'
    store.put(tiddler)
    tiddler.text = 'rev3'
    store.put(tiddler)

    retrieved = Tiddler('tiddler1', 'holder')
    retrieved = store.get(retrieved)
    assert retrieved.revision == 3
    assert retrieved.text == 'rev3'
    assert retrieved.bag == 'holder'

    retrieved.revision = 1
    retrieved = store.get(retrieved)
    assert retrieved.revision == 1
    assert retrieved.text == 'rev1'

    retrieved.revision = 2
    retrieved = store.get(retrieved)
    assert retrieved.revision == 2
    assert retrieved.text == 'rev2'


# this test now just confirms, but before the
# code was fixed it failed as expected
def test_delete_gets_revisions():
    """this relies on the previous test"""
    removed = Tiddler('tiddler1', 'holder')
    store.delete(removed)
    revision = Tiddler('tiddler1', 'holder')
    revision.revision = 2
    py.test.raises(NoTiddlerError, 'store.get(revision)')
