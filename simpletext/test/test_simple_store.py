"""
/foo.recipe
/bagname/desc
/bagname/policy
/bagname/1,2,3,4
"""
import sys
sys.path.insert(0, '.')

import os
import os.path
import shutil

from tiddlyweb.config import config
from tiddlyweb.store import Store
from simpletext import Store as SimpleText
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.user import User

def setup_module(module):
    if os.path.exists('store'):
        shutil.rmtree('store')

    module.config = config
    module.store = Store('simpletext', {'store_root': 'store'},
            environ={'tiddlyweb.config': config})

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
    loaded_recipe = store.get(loaded_recipe)
    assert loaded_recipe.desc == recipe.desc

def test_store_bag():
    bag = Bag('bag1')
    bag.desc = 'bag 1 desc'

    store.put(bag)

    # these should be _description, not description etc
    assert os.path.exists('store/bag1/description')
    assert os.path.exists('store/bag1/policy')

    loaded_bag = Bag('bag1')
    loaded_bag = store.get(loaded_bag)
    assert loaded_bag.desc == bag.desc

def test_store_user():
    user = User('testuser')
    user.set_password('testpass')
    user.add_role('testrole')

    store.put(user)

    assert os.path.exists('store/testuser.user')

    loaded_user = User('testuser')
    loaded_user = store.get(loaded_user)

    assert loaded_user.check_password('testpass')

def test_store_tiddler():
    tiddler = Tiddler('tiddler1')
    tiddler.text = 'i am tiddler 1'
    tiddler.bag = 'bag1'

    store.put(tiddler)

    assert os.path.isdir('store/bag1/tiddler1')
    assert os.path.exists('store/bag1/tiddler1/1')

    loaded_tiddler = Tiddler('tiddler1', 'bag1')
    loaded_tiddler = store.get(loaded_tiddler)
    assert loaded_tiddler.text == tiddler.text

def test_list_tiddlers():
    bag = Bag('bag1')
    bag = store.get(bag)

    tiddlers = bag.list_tiddlers()

    assert len(tiddlers) == 1
    assert 'tiddler1' in [tiddler.title for tiddler in tiddlers]

def test_list_bags():
    bags = store.list_bags()

    assert len(bags) == 1
    assert 'bag1' in [bag.name for bag in bags]

def test_list_recipes():
    recipes = store.list_recipes()

    assert len(recipes) == 1
    assert 'recipe1' in [recipe.name for recipe in recipes]

def test_list_users():
    users = store.list_users()

    assert len(users) == 1
    usernames = [user.usersign for user in users]
    assert 'testuser' in usernames
