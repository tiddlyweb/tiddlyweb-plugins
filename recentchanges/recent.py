"""
The barest beginnings of one way to do a recent 
changes plugin.

This version takes recipe or bag query parameter plus
an optional since parameter as some portion of a YYYYMMDDHHMMSS
timestamp.

Using that information the tiddlers in the recipe or bag
are traversed, including revisions, generating a list of 
tiddler information to present.

There's an argument to be made here that this could/should
be a serializer, but it was easier to experiment this way.
"""

from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.filters.select import select_parse
from tiddlyweb.filters.sort import sort_by_attribute
from tiddlyweb import control

from datetime import datetime, timedelta

def recent(environ, start_response):
    bag_name = environ['tiddlyweb.query'].get('bag', [None])[0]
    recipe_name = environ['tiddlyweb.query'].get('recipe', [None])[0]
    since = environ['tiddlyweb.query'].get('since', [None])[0]

    store = environ['tiddlyweb.store']
    tiddlers = []
    if recipe_name:
        recipe = Recipe(recipe_name)
        recipe = store.get(recipe)
        tiddlers = control.get_tiddlers_from_recipe(recipe, environ)
    if bag_name:
        bag = store.get(Bag(bag_name))
        tiddlers = bag.list_tiddlers()
    matching_tiddlers = []
    if since:
        modified_string = since
    else:
        time_object = datetime.utcnow() - timedelta(30)
        modified_string = unicode(time_object.strftime('%Y%m%d%H%M%S'))

    selector = select_parse('modified:>%s' % modified_string)
    for tiddler in tiddlers:
        stored_tiddler = store.get(tiddler)
        if selector([stored_tiddler]):
            revisions = store.list_tiddler_revisions(stored_tiddler)
            for revision in revisions:
                tiddler_revision = Tiddler(stored_tiddler.title, stored_tiddler.bag)
                tiddler_revision.revision = revision
                tiddler_revision = store.get(tiddler_revision)
                if selector([tiddler_revision]):
                    matching_tiddlers.append(tiddler_revision)

    tiddlers = sort_by_attribute('modified', matching_tiddlers, reverse=True)

    start_response('200 OK', [('Content-Type', 'text/html')])

    return ['%s:%s:%s:%s<br/>' %
            (tiddler.title, tiddler.revision, tiddler.modified, tiddler.modifier)
            for tiddler in tiddlers]

def init(config):
    config['selector'].add('/recent', GET=recent)
