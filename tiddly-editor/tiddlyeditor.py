"""
A plugin providing a web app for generating a
TiddlyWiki-based editor for a single tiddler.
"""

from tiddlyweb import control
from tiddlyweb.web.http import HTTP400, HTTP404
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import NoTiddlerError, NoBagError, NoRecipeError
from tiddlyweb.web.sendtiddlers import send_tiddlers
from tiddlyweb.web.util import tiddler_url

from tiddlyweb.web.wsgi import HTMLPresenter


def get(environ, start_response):
    """
    Using query parameters, determine the current tiddler
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

    output_bag = Bag('output', tmpbag=True)
    output_bag.add_tiddler(tiddler)

    def add_magic_tiddler(bag, title, text):
        tiddler = Tiddler(title, 'tmp')
        tiddler.text = text
        tiddler.tags = ['excludeLists']
        bag.add_tiddler(tiddler)

    add_magic_tiddler(output_bag, 'MainMenu', '[[Back to TiddlyWeb|%s]]' % tiddler_url(environ, tiddler))
    add_magic_tiddler(output_bag, 'DefaultTiddlers', '[[%s]]' % tiddler_name)
    add_magic_tiddler(output_bag, 'SiteTitle', 'Editor for %s' % tiddler_name)
    add_magic_tiddler(output_bag, 'SiteSubtitle', '')
    add_magic_tiddler(output_bag, 'SideBarOptions', '')

    for required_tiddler in environ['tiddlyweb.config'].get('tiddlyeditor_tiddlers', []):
        r_tiddler = Tiddler(required_tiddler[1], required_tiddler[0])
        r_tiddler = store.get(r_tiddler)
        if 'excludeLists' not in r_tiddler.tags:
            r_tiddler.tags.append('excludeLists')
        output_bag.add_tiddler(r_tiddler)

    environ['tiddlyweb.type'] = 'text/x-tiddlywiki'
    return send_tiddlers(environ, start_response, output_bag)


original_footer_extra = HTMLPresenter.footer_extra

def edit_link(self, environ):
    output = original_footer_extra(self, environ)
    if 'tiddlyeditor_tiddlers' in environ['tiddlyweb.config']:
        tiddler_name = environ['wsgiorg.routing_args'][1].get('tiddler_name', None)
        recipe_name = environ['wsgiorg.routing_args'][1].get('recipe_name', '')
        bag_name = environ['wsgiorg.routing_args'][1].get('bag_name', '')
        revision = environ['wsgiorg.routing_args'][1].get('revision', None)
        server_prefix = environ['tiddlyweb.config']['server_prefix']

        if tiddler_name and not revision:
            return output + '<div id="edit"><a href="%s/tiddlyeditor?tiddler=%s;bag=%s;recipe=%s">TiddlyEdit</a></div>' \
                    % (server_prefix, tiddler_name, bag_name, recipe_name)
    return output

HTMLPresenter.footer_extra = edit_link

def init(config):
    config['selector'].add('/tiddlyeditor', GET=get)
