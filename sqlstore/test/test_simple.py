
import sys
sys.path.insert(0, '.')
import sql

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.recipe import Recipe


def setup_module(module):
    engine = create_engine('sqlite:///test.db')
    Session = sessionmaker(bind=engine)
    module.session = Session()
    module.store = sql.Store()


def test_store():
    """
    An exploratory test to learn how this stuff works.
    """
    bag = Bag('bar')
    bag.policy.owner = 'cdent'
    bag.policy.read = ['cdent']
    store.bag_put(bag)

    sbag = store.session.query(sql.sBag).filter(sql.sBag.name == 'bar').one()
    assert sbag.name == bag.name
    assert sbag.policy.owner == bag.policy.owner
    assert sbag.policy.read == '["cdent"]'

    bag_d = Bag('bar')
    bag_d = store.bag_get(bag_d)

    assert bag_d.name == bag.name
    assert bag_d.policy.owner == bag.policy.owner
    assert bag_d.policy.read == bag.policy.read

    tiddler = Tiddler('tidlname', bag.name)
    tiddler.text = 'foo'
    store.tiddler_put(tiddler)

    stiddler = store.session.query(sql.sTiddler).filter(sql.sTiddler.title == 'tidlname').filter(sql.sTiddler.bag_name == 'bar').one()
    assert stiddler.title == 'tidlname'
    assert stiddler.bag_name == 'bar'
    assert len(stiddler.revisions) == 1

    tiddler = Tiddler('tidlname', bag.name)
    tiddler.text = 'foo1'
    store.tiddler_put(tiddler)

    stiddler = store.session.query(sql.sTiddler).filter(sql.sTiddler.title == 'tidlname').filter(sql.sTiddler.bag_name == 'bar').one()
    assert stiddler.title == 'tidlname'
    assert stiddler.bag_name == 'bar'
    assert len(stiddler.revisions) == 2


    tiddler_d = Tiddler('tidlname', 'bar')
    tiddler_d = store.tiddler_get(tiddler_d)

    assert tiddler_d.text == tiddler.text

    tiddlers = store.list_tiddler_revisions(tiddler_d)
    assert len(tiddlers) == 2

    store.tiddler_delete(tiddler_d)
    tiddler_d = store.tiddler_get(tiddler_d)
