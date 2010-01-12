"""
Test the ramstore.
"""
import sys
sys.path.insert(0, '') # need for the Store call below

from wsgi_intercept import httplib2_intercept
import wsgi_intercept
import httplib2

import py.test

from tiddlyweb import control
from tiddlyweb.config import config
from tiddlyweb.web import serve
from tiddlyweb.store import Store, NoTiddlerError
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler

def setup_module(module):
    module.store = Store('ramstore', {}, {})
    config['server_store'] = ['ramstore', {}]
    def app_fn():
        return serve.load_app()
    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('our_test_domain', 8001, app_fn)

def test_store_bag():
    bag_in = Bag('bagone')
    bag_in.desc = 'bag description'
    bag_in.policy.read = ['reader']
    bag_in.policy.write = ['writer']

    store.put(bag_in)

    bag_out = store.get(Bag('bagone'))

    assert bag_out.name == bag_in.name

def test_get_bag():
    """
    Make sure we are in a different scope.
    """
    bag_out = store.get(Bag('bagone'))
    assert bag_out.name == 'bagone'
    assert bag_out.desc == 'bag description'
    assert bag_out.policy.read == ['reader']
    assert bag_out.policy.write == ['writer']

def test_list_bags():
    for i in xrange(50):
        store.put(Bag(str(i)))

    bags = store.list_bags()

    assert len(bags) == 51 # bagone is still in there
    assert bags[-2].name == '9' # lexical sort

def test_web_bag():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/bags/bagone',
            method='GET')

    assert response['status'] == '200'
    assert 'bag description' in content

def test_store_recipe():
    recipe_in = Recipe('recipeone')
    recipe_in.desc = 'recipe description'

    store.put(recipe_in)

    recipe_out = store.get(Recipe('recipeone'))

    assert recipe_out.name == recipe_in.name

def test_get_recipe():
    """
    Make sure we are in a different scope.
    """
    recipe_out = store.get(Recipe('recipeone'))
    assert recipe_out.name == 'recipeone'
    assert recipe_out.desc == 'recipe description'

def test_list_recipes():
    for i in xrange(50):
        store.put(Recipe(str(i)))

    recipes = store.list_recipes()

    assert len(recipes) == 51 # recipeone is still in there
    assert recipes[-2].name == '9' # lexical sort

def test_web_recipe():
    http = httplib2.Http()
    response, content = http.request('http://our_test_domain:8001/recipes/recipeone',
            method='GET')

    assert response['status'] == '200'
    assert 'recipe description' in content

def test_put_tiddler():
    tiddler_in = Tiddler('tiddlerone', 'bagone')
    tiddler_in.text = 'hello'

    store.put(tiddler_in)

    tiddler_out = store.get(Tiddler('tiddlerone', 'bagone'))
    assert tiddler_out.text == 'hello'
    assert tiddler_in.text == tiddler_out.text

def test_bags_tiddlers():
    for i in xrange(50):
        store.put(Tiddler(str(i), 'bagone'))
    bag = store.get(Bag('bagone'))
    tiddlers = list(control.get_tiddlers_from_bag(bag))
    assert len(tiddlers) == 51

def test_tiddler_revisions():
    for i in xrange(50):
        store.put(Tiddler('revised', 'bagone'))

    tiddler = store.get(Tiddler('revised', 'bagone'))
    assert tiddler.revision == 50

    revisions = store.list_tiddler_revisions(Tiddler('revised', 'bagone'))
    assert len(revisions) == 50
    assert revisions[0] == 50
    assert revisions[-1] == 1

def test_delete_recipe():
    recipes = store.list_recipes()
    length = len(recipes)
    recipe = recipes[0]

    assert length > 0

    store.delete(recipe)
    recipes = store.list_recipes()

    assert len(recipes) == length - 1

def test_delete_bag():
    bags = store.list_bags()
    length = len(bags)
    bag = bags[0]

    assert length > 0

    store.delete(bag)
    bags = store.list_bags()

    assert len(bags) == length - 1

def test_delete_tiddler():
    tiddler = Tiddler('revised', 'bagone')
    store.delete(tiddler)

    py.test.raises(NoTiddlerError, 'store.get(tiddler)')

def test_search():
    tiddlers = store.search('hello')

    assert len(tiddlers) == 1
    assert tiddlers[0].bag == 'bagone'
    assert tiddlers[0].title == 'tiddlerone'
