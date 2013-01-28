"""
A plugin providing a web app for generating a
TiddlyWiki-based editor for a single tiddler.
"""

from httpexceptor import HTTP400, HTTP404

from tiddlyweb.control import determine_bag_from_recipe
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.collections import Tiddlers
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import NoTiddlerError, NoBagError, NoRecipeError
from tiddlyweb.serializations.html import Serialization as HTML
from tiddlyweb.web.sendtiddlers import send_tiddlers
from tiddlyweb.web.util import tiddler_url


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
            tiddler.bag = determine_bag_from_recipe(recipe,
                    tiddler).name
            tiddler.recipe = recipe.name
        except NoRecipeError, exc:
            raise HTTP404('unable to edit %s, recipe %s not found: %s'
                    % (tiddler.title, recipe_name, exc))
        except NoBagError, exc:
            raise HTTP404('unable to edit %s: %s' % (tiddler.title, exc))

    bag = Bag(tiddler.bag)
    try:
        tiddler = store.get(tiddler)
        bag = store.get(bag)
    except (NoTiddlerError, NoBagError), exc:
        raise HTTP404('tiddler %s not found: %s' % (tiddler.title, exc))

    bag.policy.allows(usersign, 'write')

    output_tiddlers = Tiddlers()
    output_tiddlers.add(tiddler)

    def add_magic_tiddler(title, text):
        tiddler = Tiddler(title, 'tmp')
        tiddler.text = text
        tiddler.tags = ['excludeLists']
        output_tiddlers.add(tiddler)

    add_magic_tiddler('MainMenu',
            '[[Back to TiddlyWeb|%s]]' % tiddler_url(environ, tiddler))
    add_magic_tiddler('DefaultTiddlers', '[[%s]]' % tiddler_name)
    add_magic_tiddler('SiteTitle', 'Editor for %s' % tiddler_name)
    add_magic_tiddler('SiteSubtitle', '')
    add_magic_tiddler('SideBarOptions', '')

    for required_tiddler in environ['tiddlyweb.config'].get(
            'tiddlyeditor_tiddlers', []):
        r_tiddler = Tiddler(required_tiddler[1], required_tiddler[0])
        r_tiddler = store.get(r_tiddler)
        if 'excludeLists' not in r_tiddler.tags:
            r_tiddler.tags.append('excludeLists')
        output_tiddlers.add(r_tiddler)

    environ['tiddlyweb.type'] = 'text/x-tiddlywiki'
    return send_tiddlers(environ, start_response, output_tiddlers)


class Serialization(HTML):

    def _footer(self):
        """
        Add editor to the footer.
        """

        output = ''
        # Not using tiddlyweb.web.util:get_route_value to avoid
        # ValueError
        routing_args = self.environ['wsgiorg.routing_args'][1]
        config = self.environ['tiddlyweb.config']
        if 'tiddlyeditor_tiddlers' in config:
            tiddler_name = routing_args.get('tiddler_name', None)
            recipe_name = routing_args.get('recipe_name', '')
            bag_name = routing_args.get('bag_name', '')
            revision = routing_args.get('revision', None)
            server_prefix = config['server_prefix']

            if tiddler_name and not revision:
                output = """
<div id="edit">
    <a href="%s/tiddlyeditor?tiddler=%s;bag=%s;recipe=%s">TiddlyEdit</a>
</div>
""" % (server_prefix, tiddler_name, bag_name, recipe_name)
        original_footer = HTML._footer(self)
        if output:
            head, sep, tail = original_footer.partition('<div id="badge">')
            return head + output + sep + tail
        return original_footer


def init(config):
    if 'selector' in config:
        config['selector'].add('/tiddlyeditor', GET=get)
        config['serializers']['text/html'] = [__name__,
                'text/html; charset=UTF-8']
