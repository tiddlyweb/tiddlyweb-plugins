

import sys
import shutil
import py.test

from tiddlyweb.store import Store
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.config import config
from tiddlyweb.manage import handle
from tiddlywebplugins.utils import get_store
from tiddlywebplugins.recipeupdater import init


def setup_module(module):
    try:
        shutil.rmtree('store')
    except:
        pass
    module.store = get_store(config)
    init(config)
    base_recipe = Recipe('hi')
    base_recipe.set_recipe([
        ('system', ''),
        ('stuff', 'select=title:monkey'),
        ('things', '')])
    module.store.put(base_recipe)
    sys.exit = boring_exit


class InternalExit(Exception):
    pass


def boring_exit(value):
    raise InternalExit()


def test_simple_replace():
    handle(['', 'recipeupdate', '/bags/stuff/tiddlers?select=title:monkey',
        '/bags/faster/tiddlers'])

    recipe = store.get(Recipe('hi'))
    recipelist = recipe.get_recipe()

    assert ['faster', ''] in recipelist
    assert ['stuff', 'select=title:monkey'] not in recipelist


def test_double_replace():
    handle(['', 'recipeupdate', '/bags/faster/tiddlers',
        '/bags/thanks/tiddlers?sort=modified',
        '/bags/collapse/tiddlers'])

    recipe = store.get(Recipe('hi'))
    recipelist = recipe.get_recipe()

    assert ['faster', ''] not in recipelist
    assert ['thanks', 'sort=modified'] in recipelist
    assert ['collapse', ''] in recipelist


def test_bad_input():
    py.test.raises(InternalExit, "handle(['', 'recipeupdate', '/bags/collapse/tiddlers', '/bags/thanks/tiddlers?sort=modified', '/bags/tiddlers'])")
    py.test.raises(InternalExit, "handle(['', 'recipeupdate', '/bags/tiddlers', '/bags/thanks/tiddlers?sort=modified', '/bags/collapse/tiddlers'])")

