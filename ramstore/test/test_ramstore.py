"""
Test the ramstore.
"""
import sys
sys.path.insert(0, '') # need for the Store call below

from wsgi_intercept import httplib2_intercept
import wsgi_intercept
import httplib2

from tiddlyweb.config import config
from tiddlyweb.web import serve
from tiddlyweb.store import Store
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe

def setup_module(module):
    module.store = Store('ramstore', {})
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
