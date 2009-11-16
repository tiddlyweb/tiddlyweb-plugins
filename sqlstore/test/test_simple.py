
import sys
sys.path.insert(0, '.')

import sql

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.user import User
from tiddlyweb.store import Store
from tiddlyweb.config import config

from sqlalchemy.sql import and_, or_, join, text
from sqlalchemy.orm import aliased

EMPTY_TIDDLER=Tiddler('empty','empty')


def setup_module(module):
    module.store = Store('sql', environ={'tiddlyweb.config': config})


def test_store():
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
    tiddler.modifier = u'nancy'
    store.put(tiddler)

    stiddler = store.storage.session.query(sql.sTiddler).filter(sql.sTiddler.title == u'tidlname').filter(sql.sTiddler.bag_name == u'bar').one()
    assert stiddler.title == 'tidlname'
    assert stiddler.bag_name == 'bar'
    assert len(stiddler.revisions) == 1

    tiddler = Tiddler(u'tidlname', bag.name)
    tiddler.text = u'foo1'
    tiddler.modifier = u'karl'
    store.put(tiddler)

    stiddler = store.storage.session.query(sql.sTiddler).filter(sql.sTiddler.title == u'tidlname').filter(sql.sTiddler.bag_name == u'bar').one()
    assert stiddler.title == u'tidlname'
    assert stiddler.bag_name == u'bar'
    assert len(stiddler.revisions) == 2


    tiddler_d = Tiddler(u'tidlname', u'bar')
    tiddler_d = store.get(tiddler_d)

    assert tiddler_d.text == tiddler.text
    assert tiddler_d.modifier == u'karl'
    assert tiddler_d.creator == u'nancy'

    tiddlers = store.list_tiddler_revisions(tiddler_d)
    assert len(tiddlers) == 2

    store.delete(tiddler_d)
    #tiddler_d = store.get(tiddler_d)

def test_revision_search():
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

def test_put_get_bag():
    bag = Bag('testone')
    bag.policy.read = ['cdent']
    store.put(bag)

    read_bag = Bag('testone')
    read_bag.skinny = True
    read_bag = store.get(read_bag)

    assert read_bag.policy.read == ['cdent']

def test_put_get_recipe():
    recipe = Recipe('testone')
    recipe.policy.read = ['cdent']
    store.put(recipe)

    read_recipe = Recipe('testone')
    read_recipe.skinny = True
    read_recipe = store.get(read_recipe)

    assert read_recipe.policy.read == ['cdent']

def test_put_get_user():
    user = User('testone')
    user.add_role('monkey')
    store.put(user)

    read_user = User('testone')
    read_user = store.get(read_user)

    assert read_user.list_roles() == ['monkey']

def test_put_get_tiddler():
    bag = Bag(u'test1')
    store.put(bag)

    for i in xrange(5):
        tiddler = Tiddler(u'tid1', u'test1')
        tiddler.text = u'hello'
        tiddler.tags = [u'five',u'six']
        tiddler.fields[u'radar'] = u'green'

        store.put(tiddler)

    read_tiddler = Tiddler('tid1', 'test1')
    read_tiddler = store.get(read_tiddler)

    assert read_tiddler.title == 'tid1'
    assert read_tiddler.fields['radar'] == 'green'

