
import sys
sys.path.insert(0, '.')

import sql

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.store import Store
from tiddlyweb.config import config

from sqlalchemy.sql import and_, or_, join, text
from sqlalchemy.orm import aliased

EMPTY_TIDDLER=Tiddler('empty','empty')


def setup_module(module):
    module.store = Store('sql', environ={'tiddlyweb.config': config})


def xtest_store():
    """
    An exploratory test to learn how this stuff works.
    """
    bag = Bag(u'bar')
    bag.policy.owner = u'cdent'
    bag.policy.read = [u'cdent']
    store.put(bag)

    sbag = store.storage.session.query(sql.sBag).filter(sql.sBag.name == u'bar').one()
    assert sbag.name == bag.name
    assert sbag.policy.owner == bag.policy.owner
    assert sbag.policy.read == u'["cdent"]'

    bag_d = Bag(u'bar')
    bag_d = store.get(bag_d)

    assert bag_d.name == bag.name
    assert bag_d.policy.owner == bag.policy.owner
    assert bag_d.policy.read == bag.policy.read

    tiddler = Tiddler(u'tidlname', bag.name)
    tiddler.text = u'foo'
    store.put(tiddler)

    stiddler = store.storage.session.query(sql.sTiddler).filter(sql.sTiddler.title == u'tidlname').filter(sql.sTiddler.bag_name == u'bar').one()
    assert stiddler.title == 'tidlname'
    assert stiddler.bag_name == 'bar'
    assert len(stiddler.revisions) == 1

    tiddler = Tiddler(u'tidlname', bag.name)
    tiddler.text = u'foo1'
    store.put(tiddler)

    stiddler = store.storage.session.query(sql.sTiddler).filter(sql.sTiddler.title == u'tidlname').filter(sql.sTiddler.bag_name == u'bar').one()
    assert stiddler.title == u'tidlname'
    assert stiddler.bag_name == u'bar'
    assert len(stiddler.revisions) == 2


    tiddler_d = Tiddler(u'tidlname', u'bar')
    tiddler_d = store.get(tiddler_d)

    assert tiddler_d.text == tiddler.text

    tiddlers = store.list_tiddler_revisions(tiddler_d)
    assert len(tiddlers) == 2

    store.delete(tiddler_d)
    #tiddler_d = store.get(tiddler_d)

def xtest_revision_search():
    store.put(Bag(u'revs'))

    tiddler = Tiddler(u'r1', u'revs')
    tiddler.text = u'foo'
    tiddler.fields[u'huntsman'] = u'hello'
    tiddler.fields[u'target'] = u'monkey'
    store.put(tiddler)

    rtiddler = store.get(Tiddler(u'r1', u'revs'))
    assert rtiddler.text == u'foo'


    tiddler = Tiddler(u'r1', u'revs')
    tiddler.text = u'bar'
    tiddler.fields[u'huntsman'] = u'goodbye'
    tiddler.fields[u'target'] = u'cow'
    store.put(tiddler)

    rtiddler = store.get(Tiddler(u'r1', u'revs'))
    assert rtiddler.text == u'bar'

    tiddlers = list(store.search(u'foo'))
    assert len(tiddlers) == 0

    tiddlers = list(store.search(u'bar'))
    assert len(tiddlers) == 1

    tiddlers = list(store.search(u'hello'))
    assert len(tiddlers) == 0

    tiddlers = list(store.search(u'goodbye'))
    assert len(tiddlers) == 1

    tiddlers = list(store.search(u'target:cow huntsman:goodbye bar'))
    assert len(tiddlers) == 1

    tiddlers = list(store.search(u'target:cow huntsman:goodbye foo'))
    assert len(tiddlers) == 0

def test_more_data():
    for j in xrange(10):
        for i in xrange(10):
            tiddler = Tiddler(u'r1', u'revs')
            tiddler.text = u'bar%s' % i
            tiddler.fields[u'huntsman'] = u'goodbye'
            store.put(tiddler)

        for i in xrange(10):
            tiddler = Tiddler(u'r1%s' % i, u'revs')
            tiddler.text = u'bar'
            tiddler.fields[u'huntsman'] = u'goodbye'
            tiddler.fields[u'target'] = u'cow'
            store.put(tiddler)

    tiddlers = list(store.search(u'target:cow huntsman:goodbye bar'))
    assert len(tiddlers) == 10
    tiddler = store.get(tiddlers[0])
    assert tiddler.revision == 10
