"""
/foo.recipe
/bagname/desc
/bagname/policy
/bagname/1,2,3,4
"""
import sys
sys.path.append('.')

import os
import os.path

from tiddlyweb.config import config
from tiddlyweb.store import Store
from simpletext import Store as SimpleText
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler

def setup_module(module):
    module.config = config
    module.store = Store('simpletext', environ={'tiddlyweb.config': config})

def test_get_store():

    assert type(store.storage) == SimpleText

def test_store_exists():
    assert os.path.exists('store')

def test_store_recipe():
    recipe = Recipe('recipe1')
    recipe.desc = 'recipe 1 desc'
    recipe.set_recipe([
        ['bag1', '']
        ])

    store.put(recipe)

    assert os.path.exists('store/recipe1.recipe')

    loaded_recipe = Recipe('recipe1')
    store.get(loaded_recipe)
    assert loaded_recipe.desc == recipe.desc

def test_store_bag():
    bag = Bag('bag1')
    bag.desc = 'bag 1 desc'

    store.put(bag)

    # these should be _description, not description etc
    assert os.path.exists('store/bag1/description')
    assert os.path.exists('store/bag1/policy')

    loaded_bag = Bag('bag1')
    store.get(loaded_bag)
    assert loaded_bag.desc == bag.desc

def test_store_tiddler():
    tiddler = Tiddler('tiddler1')
    tiddler.text = 'i am tiddler 1'
    tiddler.bag = 'bag1'

    store.put(tiddler)

    assert os.path.isdir('store/bag1/tiddler1')
    assert os.path.exists('store/bag1/tiddler1/1')

    loaded_tiddler = Tiddler('tiddler1', 'bag1')
    store.get(loaded_tiddler)
    assert loaded_tiddler.text == tiddler.text

def test_list_tiddlers():
    bag = Bag('bag1')
    store.get(bag)

    tiddlers = bag.list_tiddlers()

    assert len(tiddlers) == 1
    assert 'tiddler1' in [tiddler.title for tiddler in tiddlers]
