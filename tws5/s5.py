"""
TiddlyWeb serializer for presenting some tiddlers
as an S5 slideshow. Requires jinja2 and the static
plugin. The contents of the templates dir and static
dir are required.

When viewing any list of tiddlers, or any single tiddler
if you append '.s5' to the end of the URL you will get
an HTML file that is formatted as an S5

   http://meyerweb.com/eric/tools/s5/

slideshow. The required javascript and CSS are in the
static dir, the basic HTML framework in in the temmplates
dir.

If the list of tiddlers includes some special tiddlers their
text content is used for some things:

    * SiteTitle: The title of the presentation
    * SiteSubtitle: The subtitle of the presentation
    * S5Presenter: The person giving the presentation
    * S5Affiliation: Their affiliation
    * S5TimeLocation: when and where of the presentation

If multiple tiddlers of the same name (only possible when
viewing revisons) the last is used. Using the S5 serialization
when viewing revisions doesn't make much sense.

Slides other than the title slide are made up of tiddlers
in the list (except those listed above). The title of
the tiddler is used as the title of the slide. The text of
the tiddler is rendered to HTML.

S5 has support for notes to be associated with a handout
display of each slide. This is not currently used but we
can probably figure out a fun way to use it.
"""

from jinja2 import Environment, FileSystemLoader

import logging

from tiddlyweb.wikitext import render_wikitext
from tiddlyweb.serializations import SerializationInterface
from tiddlyweb.model.bag import Bag


EXTENSION_TYPES = { 's5': 'application/x-s5+html' }
SERIALIZERS = {
        'application/x-s5+html': ['s5', 'text/html; charset=UTF-8']
        }

DEFAULT_TITLE = 'S5 Title'
DEFAULT_SUBTITLE = 'S5 Subtitle'
DEFAULT_PRESENTER = 'S5 Presenter'
DEFAULT_AFFILIATION = 'S5 Affiliation'
DEFAULT_TIME_LOCATION = 'S5 Time Location'


class Serialization(SerializationInterface):

    def __init__(self, environ=None):
        if environ is None:
            environ = {}
        self.environ = environ
        self._init()

    def _init(self):
        template_env = Environment(loader=FileSystemLoader('templates'))
        self.template = template_env.get_template('s5.html')

    def tiddler_as(self, tiddler):
        bag = Bag('tmpbag', tmpbag=True)
        bag.add_tiddler(tiddler)
        return self.list_tiddlers(bag)

    def list_tiddlers(self, bag):
        tiddlers = bag.list_tiddlers()
        title = DEFAULT_TITLE
        subtitle = DEFAULT_SUBTITLE
        presenter = DEFAULT_PRESENTER
        affiliation = DEFAULT_AFFILIATION
        time_location = DEFAULT_TIME_LOCATION
        slides = {}
        slide_order = None
        original_slide_order = []
        for tiddler in tiddlers:
            if tiddler.title == 'SiteTitle':
                title = tiddler.text
                continue
            if tiddler.title == 'SiteSubtitle':
                subtitle = tiddler.text
                continue
            if tiddler.title == 'S5Presenter':
                presenter = tiddler.text
                continue
            if tiddler.title == 'S5Affiliation':
                affiliation = tiddler.text
                continue
            if tiddler.title == 'S5TimeLocation':
                time_location = render_wikitext(tiddler, self.environ)
                continue
            if tiddler.title == 'S5Sort':
                slide_order = tiddler.text.split('\n')
                continue
            slides[tiddler.title] = tiddler
            original_slide_order.append(tiddler.title)
            tiddler.html = render_wikitext(tiddler, self.environ)

        if slide_order is None:
            slide_order = original_slide_order

        return self.template.render(slides=slides,
                slide_order=slide_order,
                title=title,
                subtitle=subtitle,
                presenter=presenter,
                affiliation=affiliation,
                time_location=time_location)


def init(config):
    config['extension_types'].update(EXTENSION_TYPES)
    config['serializers'].update(SERIALIZERS)
