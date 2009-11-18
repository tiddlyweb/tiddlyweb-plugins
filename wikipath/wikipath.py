"""
Quick and dirty way to have a path to a recipe that "is"
the wiki. That is, by going to this URL you are saying,
give me a wiki that is identified by this recipe name.

The default selector path is /wiki/{recipe_name}. It can
be changed by setting wikipath in tiddlywebconfig.py.

If the selector path is / then / /bags /recipes will
still work correctly, as they come before /{recipe_name}
in the selector matching system. Note this means you
can't get to a wiki named bags or recipes by this path.
"""

from tiddlywebplugins.utils import replace_handler
from tiddlyweb.web.handler.recipe import get_tiddlers

def init(config):
    wikipath = config.get('wikipath', '/wiki')
    if wikipath == '/':
        config['selector'].add('/{recipe_name}',GET=wiki_handler)
    else:
        config['selector'].add(wikipath + '/{recipe_name}', GET=wiki_handler)


def wiki_handler(environ, start_response):
    environ['tiddlyweb.type'] = 'text/x-tiddlywiki'
    return get_tiddlers(environ, start_response)


