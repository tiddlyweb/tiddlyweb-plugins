"""
A plugin providing  web app for generating a
tiddlywiki based editor for a single Tiddler.
"""

import urllib

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
    Using query parameters, determine the
    tiddler we are currently working with
    and produce an editor for it.
    """
    usersign = environ['tiddlyweb.usersign']
    try:
        tiddler_name = environ['tiddlyweb.query'].get('tiddler', [''])[0]
        recipe_name = environ['tiddlyweb.query'].get('recipe', [''])[0]
        bag_name = environ['tiddlyweb.query'].get('bag', [''])[0]
        tiddler_name = unicode(urllib.unquote(tiddler_name), 'utf-8')
        bag_name = unicode(urllib.unquote(bag_name), 'utf-8')
        recipe_name = unicode(urllib.unquote(recipe_name), 'utf-8')
    except (KeyError, IndexError):
        raise HTTP400('tiddler, recipe and bag query strings required')

    store = environ['tiddlyweb.store']

    tiddler = Tiddler(tiddler_name)
    if bag_name:
        tiddler.bag = bag_name
    else:
        recipe = Recipe(recipe_name)
        try:
            store.get(recipe)
            tiddler.bag = control.determine_tiddler_bag_from_recipe(recipe, tiddler).name
            tiddler.recipe = recipe.name
        except NoRecipeError, exc:
            raise HTTP404('unable to edit %s, recipe %s not found: %s' % (tiddler.title, recipe_name, exc))
        except NoBagError, exc:
            raise HTTP404('unable to edit %s: %s' % (tiddler.title, exc))

    bag = Bag(tiddler.bag)
    try:
        store.get(tiddler)
        store.get(bag)
    except (NoTiddlerError, NoBagError), exc:
        raise HTTP404('tiddler %s not found: %s' % (tiddler.title, exc))

    bag.policy.allows(usersign, 'write')

    output_bag = Bag('output', tmpbag=True)
    output_bag.add_tiddler(tiddler)

    editor_tiddler = Tiddler('EditorMenu')
    editor_tiddler.text = '![[Back to TiddlyWeb|%s]]' % tiddler_url(environ, tiddler)
    output_bag.add_tiddler(editor_tiddler)

    default_tiddler = Tiddler('DefaultTiddlers')
    default_tiddler.text = 'EditorMenu\n%s' % tiddler_name
    output_bag.add_tiddler(default_tiddler)

    site_title_tiddler = Tiddler('SiteTitle')
    site_title_tiddler.text = 'Editor for %s' % tiddler_name
    site_subtitle_tiddler = Tiddler('SiteSubtitle')
    site_subtitle_tiddler.text = ''
    output_bag.add_tiddler(site_title_tiddler)
    output_bag.add_tiddler(site_subtitle_tiddler)

    for required_tiddler in environ['tiddlyweb.config'].get('tiddlyeditor_tiddlers', []):
        r_tiddler = Tiddler(required_tiddler[1], required_tiddler[0])
        store.get(r_tiddler)
        output_bag.add_tiddler(r_tiddler)

    environ['tiddlyweb.type'] = 'text/x-tiddlywiki'
    return send_tiddlers(environ, start_response, output_bag)


def edit_link(self, environ):
    output = self.original_footer_extra(environ)
    if 'tiddlyeditor_tiddlers' in environ['tiddlyweb.config']:
        tiddler_name = environ['wsgiorg.routing_args'][1].get('tiddler_name', None)
        recipe_name = environ['wsgiorg.routing_args'][1].get('recipe_name', '')
        bag_name = environ['wsgiorg.routing_args'][1].get('bag_name', '')
        revision = environ['wsgiorg.routing_args'][1].get('revision', None)

        if tiddler_name and not revision:
            return output + '<div id="edit"><a href="/tiddlyeditor?tiddler=%s;bag=%s;recipe=%s">Edit</a></div>' \
                    % (tiddler_name, bag_name, recipe_name)
    return output

HTMLPresenter.original_footer_extra = HTMLPresenter.footer_extra
HTMLPresenter.footer_extra = edit_link

def init(config):
    config['selector'].add('/tiddlyeditor', GET=get)

