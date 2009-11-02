"""
A quick hack to parse CGI form fields into fields on a
tiddler.

TODO:

    better bag name handling
    ensuring the bag exists
    redirect to somewhere useful

"""

from tiddlyweb.model.tiddler import Tiddler

from tiddlyweb.web.http import HTTP302

SKIP_FIELDS = [] # add string fields that we don't want in the tiddler data
TARGET_BAG = 'bag0' # XXX this ought to come from the form. Existence assumed.


def init(config):
    config['selector'].add('/submit', POST=handler)


def handler(environ, start_response):
    input = environ['tiddlyweb.query']
    store = environ['tiddlyweb.store']

    # deal with python cgi packaging
    for field in input:
        if field in SKIP_FIELDS:
            continue
        input[field] = input[field][0]

    # need this to come in on the form input
    tiddler_title = input['tiddler_title']
    del input['tiddler_title']

    tiddler = Tiddler(tiddler_title, TARGET_BAG) # XXX is this the bag you want?
    try:
        tiddler.text = input['text']
        del input['text']
    except KeyError:
        tiddler.text = ''
    tiddler.fields = input

    store.put(tiddler)

    url = '/' # XXX replace with real url
    raise HTTP302(url)
