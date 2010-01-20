"""
Test reading in a tiddler div from a TiddlyWiki document.
"""

import re

import html5lib

from html5lib import treebuilders

from tiddlyweb.config import config
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import Store

from tiddlywebplugins.twimport import (_get_tiddler_from_div,
        _expand_recipe)


BAGNAME = 'test'
SAMPLE_BASIC_TIDDLER = """
<div title="GettingStarted">
<pre>To get started with this blank [[TiddlyWiki]], you'll need to modify the following tiddlers:
* [[SiteTitle ]] & [[SiteSubtitle]]: The title and subtitle of the site, as shown above (after saving, they will also appear in the browser title bar)
* [[MainMenu]]: The menu (usually on the left)
* [[DefaultTiddlers]]: Contains the names of the tiddlers that you want to appear when the TiddlyWiki is opened You'll also need to enter your username for signing your edits: <<option txtUserName>></pre>
</div>
"""

SAMPLE_EMPTY_TIDDLER = """
<div title="GettingStopped">
<pre>
</pre>
</div>
"""


def setup_module(module):
    module.store = Store(config['server_store'][0], config['server_store'][1], environ={'tiddlyweb.config': config})
    bag = Bag(BAGNAME)
    module.store.put(bag)


def test_import_simple_tiddler_div():
    div = _parse(SAMPLE_BASIC_TIDDLER)
    assert div.getAttribute('title') == 'GettingStarted'

    tiddler = _get_tiddler_from_div(div)

    assert tiddler.title == 'GettingStarted'
    assert 'as shown above (after' in tiddler.text


def test_import_empty_tiddler_div():
    div = _parse(SAMPLE_EMPTY_TIDDLER)
    assert div.getAttribute('title') == 'GettingStopped'

    tiddler = _get_tiddler_from_div(div)
    tiddler.bag = BAGNAME
    store.put(tiddler)

    tiddler = Tiddler('GettingStopped', BAGNAME)
    tiddler = store.get(tiddler)
    assert tiddler.title == 'GettingStopped'
    assert tiddler.text == ''


def test_handle_timestamps():
    tiddler_element = """
    <div title="Foo" created="200901011200" modified="200911261330">
    <pre></pre>
    </div>
    """
    div = _parse(tiddler_element)
    tiddler = _get_tiddler_from_div(div)
    assert tiddler.created == '200901011200'
    assert tiddler.modified == '200911261330'

    tiddler_element = """
    <div title="Foo" created="200901011200">
    <pre></pre>
    </div>
    """
    div = _parse(tiddler_element)
    tiddler = _get_tiddler_from_div(div)
    assert tiddler.created == '200901011200'
    assert tiddler.modified == '200901011200'

    tiddler_element = """
    <div title="Foo" modified="200911261330">
    <pre></pre>
    </div>
    """
    div = _parse(tiddler_element)
    tiddler = _get_tiddler_from_div(div)
    assert tiddler.created == ''
    assert tiddler.modified == '200911261330'

    tiddler_element = """
    <div title="Foo">
    <pre></pre>
    </div>
    """
    div = _parse(tiddler_element)
    tiddler = _get_tiddler_from_div(div)
    assert re.match('\d{12}', tiddler.modified)
    assert tiddler.created == ''


def test_omit_reserved_fields():
    tiddler_element = """
    <div title="Hello World" changecount="3" title="bar"
        server.host="example.org" server.workspace="default"
        custom="baz">
    <pre>lorem ipsum
    dolor sit amet</pre>
    </div>
    """
    div = _parse(tiddler_element)
    assert div.getAttribute('title') == 'Hello World'

    tiddler = _get_tiddler_from_div(div)

    assert tiddler.title == 'Hello World'
    assert tiddler.fields['custom'] == 'baz'
    assert 'title' not in tiddler.fields
    assert 'server.host' not in tiddler.fields
    assert 'server.workspace' not in tiddler.fields
    assert 'changecount' not in tiddler.fields


def test_handle_recipe_basic():
    urls = _expand_recipe("""tiddler: monkey/pirate.tiddler
""", 'http://example.com/')
    assert urls == ['http://example.com/monkey/pirate.tiddler']


def test_handle_recipe_urls():
    urls = _expand_recipe("""tiddler: %7Emonkey/pirate.tiddler
tiddler: %7Especial/thing.tid
""", 'http://example.com/')
    assert urls == ['http://example.com/%7Emonkey/pirate.tiddler', 'http://example.com/%7Especial/thing.tid']


def test_handle_recipe_utf8():
    """
    handle_recipe takes a base url and some utf-8 encoded
    content that is a recipe. It returns a list of urls.
    """
    urls = _expand_recipe("""tiddler: monkey/%s/pirate.tiddler
plugin: special/%s/thing.js
""" % ('\xE2\x84\xA2', '\xE2\x84\xA2'), 'http://example.com/')
    assert urls == ['http://example.com/monkey/%E2%84%A2/pirate.tiddler', 'http://example.com/special/%E2%84%A2/thing.js']


def test_handle_recipe_from_unicode():
    recipe = u"""tiddler: monkey/%s/pirate.tiddler
tiddler: special/%s/thing.tid
""" % (u'\u2122', u'\u2122')
    recipe = recipe.encode('utf-8')
    urls = _expand_recipe(recipe, 'http://example.com/')
    assert urls == ['http://example.com/monkey/%E2%84%A2/pirate.tiddler', 'http://example.com/special/%E2%84%A2/thing.tid']


def test_handle_recipe_plugin():
    recipe = u'plugin: monkey/pirate.tid'
    recipe = recipe.encode('utf-8')
    urls = _expand_recipe(recipe, 'http://example.com/')
    assert urls == ['http://example.com/monkey/pirate.tid']


def _parse(content):
    parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder('dom'))
    dom = parser.parse(content)
    tiddler_div = dom.getElementsByTagName('div')[0]
    return tiddler_div
