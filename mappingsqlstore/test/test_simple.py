

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.config import config
from tiddlyweb.store import Store, NoBagError, NoTiddlerError

import py.test

def test_bag_get():
    store = Store('mappingsql', {'tiddlyweb.config': config})
    bag = Bag('avox')
    assert len(bag.list_tiddlers()) == 0

    bag = store.get(bag)
    assert len(bag.list_tiddlers()) == 1
    assert "NONE" in bag.policy.write


def test_bag_get_wrong():
    store = Store('mappingsql', {'tiddlyweb.config': config})
    bag = Bag('test')
    py.test.raises(NoBagError, 'bag = store.get(bag)')


def test_tiddler_get():
    store = Store('mappingsql', {'tiddlyweb.config': config})
    tiddler = Tiddler('monkey', 'avox')
    tiddler = store.get(tiddler)
    assert tiddler.fields['field_one'] == 'fat'


def test_tiddler_not():
    store = Store('mappingsql', {'tiddlyweb.config': config})
    tiddler = Tiddler('ape', 'avox')
    py.test.raises(NoTiddlerError, 'tiddler = store.get(tiddler)')


def test_tiddler_not_bag():
    store = Store('mappingsql', {'tiddlyweb.config': config})
    tiddler = Tiddler('monkey', 'test')
    py.test.raises(NoBagError, 'tiddler = store.get(tiddler)')


def test_tiddler_limit_field():
    store = Store('mappingsql', {'tiddlyweb.config': config})
    tiddler = Tiddler('monkey', 'avox')
    tiddler = store.get(tiddler)
    assert tiddler.fields['field_one'] == 'fat'
    assert 'field_three' not in tiddler.fields
    assert 'field_two' not in tiddler.fields

    store = Store('mappingsql', {
        'tiddlyweb.config': config,
        'tiddlyweb.usersign': {'name': 'zow'}
        })
    tiddler = Tiddler('monkey', 'avox')
    tiddler = store.get(tiddler)
    assert tiddler.fields['field_one'] == 'fat'
    assert 'field_three' in tiddler.fields
    assert 'field_two' in tiddler.fields

    store = Store('mappingsql', {
        'tiddlyweb.config': config,
        'tiddlyweb.usersign': {'name': u'GUEST'}
        })
    tiddler = Tiddler('monkey', 'avox')
    tiddler = store.get(tiddler)
    assert tiddler.fields['field_one'] == 'fat'
    assert 'field_three' not in tiddler.fields
    assert 'field_two' not in tiddler.fields


def test_search():
    store = Store('mappingsql', {'tiddlyweb.config': config})
    tiddlers = list(store.search('cdent field_one:fat'))
    assert tiddlers[0].title == 'monkey'