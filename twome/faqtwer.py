"""
A thing which is sort of a faq engine.
"""

from jinja2 import Environment, FileSystemLoader
template_env = Environment(loader=FileSystemLoader('templates'))

from tiddlyweb.model.bag import Bag
from tiddlyweb.web.util import tiddler_url

from twplugins import do_html, entitle

FAQ_BAG = 'faqs'

@do_html()
@entitle('FAQ')
def faq(environ, start_response):
    store = environ['tiddlyweb.store']
    bag = Bag(FAQ_BAG)
    bag = store.get(bag)
    tiddlers = [store.get(tiddler) for tiddler in bag.list_tiddlers()]
    categorical = {}
    for tiddler in tiddlers:
        tiddler.fields['url'] = tiddler_url(environ, tiddler)
        for tag in tiddler.tags:
            try:
                categorical[tag].append(tiddler)
            except KeyError:
                categorical[tag] = [tiddler]
    try:
        requested_category = environ['wsgiorg.routing_args'][1]['category']
        all_tags = [requested_category]
    except KeyError:
        all_tags = categorical.keys()
    template = template_env.get_template('faqtop.html')
    return template.generate(
            categories=all_tags,
            info=categorical
            )


def init(config):
    config['selector'].add('/faq', GET=faq)
    config['selector'].add('/faq/{category}', GET=faq)
