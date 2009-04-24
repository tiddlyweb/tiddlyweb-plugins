"""
A quick plugin to demonstrate creating
recipes on the fly.
"""

from tiddlyweb import control
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.web.sendtiddlers import send_tiddlers

from tiddlywebplugins import require_any_user

BASE_BAG_NAME = 'system'

@require_any_user()
def dyna(environ, start_response):
    name = environ['wsgiorg.routing_args'][1].get('name', 'default')
    username = environ['tiddlyweb.usersign']['name']
    recipe = Recipe('tmp')
    recipe.set_recipe([
        [BASE_BAG_NAME, ''],
        [name, ''],
        [username, '']
        ])
    # establish the store on the recipe so that get_tiddlers_from_recipe
    # will load the bags and their tiddler lists from the store
    recipe.store = environ['tiddlyweb.store']
    tiddlers = control.get_tiddlers_from_recipe(recipe, environ)
    bag = Bag('tmp', tmpbag=True)
    bag.add_tiddlers(tiddlers)
    return send_tiddlers(environ, start_response, bag)
    

def init(config):
    config['selector'].add('/dyna/{name}', GET=dyna)
