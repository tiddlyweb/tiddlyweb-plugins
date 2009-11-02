"""
A plugin providing  web app for generating a
tiddlywiki based editor for a single Tiddler.
"""

from tiddlyweb import control
from tiddlyweb.web.http import HTTP400, HTTP404, HTTP302
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import NoTiddlerError, NoBagError, NoRecipeError
from tiddlyweb.web.util import tiddler_url

from tiddlyweb.web.wsgi import HTMLPresenter


def get(environ, start_response):
    """
    Using query parameters, determine the
    tiddler we are currently working with
    and produce an editor for it.
    """
    usersign = environ['tiddlyweb.usersign']
    try:
        tiddler_name = environ['tiddlyweb.query'].get('tiddler', [''])[0]
        recipe_name = environ['tiddlyweb.query'].get('recipe', [''])[0]
        bag_name = environ['tiddlyweb.query'].get('bag', [''])[0]
    except (KeyError, IndexError):
        raise HTTP400('tiddler, recipe and bag query strings required')

    store = environ['tiddlyweb.store']

    tiddler = Tiddler(tiddler_name)
    if bag_name:
        tiddler.bag = bag_name
    else:
        recipe = Recipe(recipe_name)
        try:
            recipe = store.get(recipe)
            tiddler.bag = control.determine_tiddler_bag_from_recipe(recipe, tiddler).name
            tiddler.recipe = recipe.name
        except NoRecipeError, exc:
            raise HTTP404('unable to edit %s, recipe %s not found: %s' % (tiddler.title, recipe_name, exc))
        except NoBagError, exc:
            raise HTTP404('unable to edit %s: %s' % (tiddler.title, exc))

    bag = Bag(tiddler.bag)
    try:
        tiddler = store.get(tiddler)
        bag = store.get(bag)
    except (NoTiddlerError, NoBagError), exc:
        raise HTTP404('tiddler %s not found: %s' % (tiddler.title, exc))

    bag.policy.allows(usersign, 'write')

    cancel_url = tiddler_url(environ, tiddler)

    server_prefix = environ['tiddlyweb.config']['server_prefix']
    environ['tiddlyweb.title'] = 'Edit %s' % tiddler.title
    start_response('200 OK', [
        ('Content-Type', 'text/html')
        ])

    return """
<form action="%s/formeditor" method="POST">
<textarea name="text" rows="10" cols="50">
%s
</textarea>
<input type="hidden" name="title" value="%s">
<input type="hidden" name="bag" value="%s">
<input type="submit">
<a href="%s">Cancel</a>
</form>
""" % (server_prefix, tiddler.text, tiddler.title, tiddler.bag, cancel_url)


def post(environ, start_response):
    usersign = environ['tiddlyweb.usersign']
    text = environ['tiddlyweb.query'].get('text', [''])[0]
    title = environ['tiddlyweb.query'].get('title', [''])[0]
    bag = environ['tiddlyweb.query'].get('bag', [''])[0]

    store = environ['tiddlyweb.store']

    tiddler = Tiddler(title, bag)
    tiddler.text = text
    tiddler.modifier = usersign['name']
    bag = Bag(bag)
    try:
        bag = store.get(bag)
    except NoBagError, exc:
        raise HTTP404('tiddler %s not found: %s' % (tiddler.title, exc))

    bag.policy.allows(usersign, 'write')
    redir_url = tiddler_url(environ, tiddler)

    store.put(tiddler)

    raise HTTP302(redir_url)


original_footer_extra = HTMLPresenter.footer_extra

def edit_link(self, environ):
    tiddler_name = environ['wsgiorg.routing_args'][1].get('tiddler_name', None)
    recipe_name = environ['wsgiorg.routing_args'][1].get('recipe_name', '')
    bag_name = environ['wsgiorg.routing_args'][1].get('bag_name', '')
    revision = environ['wsgiorg.routing_args'][1].get('revision', None)
    server_prefix = environ['tiddlyweb.config']['server_prefix']

    output = original_footer_extra(self, environ)
    if tiddler_name and not revision:
        return output + '<div id="edit"><a href="%s/formeditor?tiddler=%s;bag=%s;recipe=%s">FormEdit</a></div>' \
                % (server_prefix, tiddler_name, bag_name, recipe_name)
    return output

HTMLPresenter.footer_extra = edit_link


def init(config):
    config['selector'].add('/formeditor', GET=get, POST=post)
