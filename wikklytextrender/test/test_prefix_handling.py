
import sys
sys.path.insert(0, '.')
from wikklytextrender import render

from tiddlyweb.model.tiddler import Tiddler


def test_simple_render():
    tiddler = Tiddler('bar')
    tiddler.text = 'Hello [[monkey]]!'
    tiddler.bag = 'zoo'

    html = render(tiddler, {})
    assert 'href="/bags/zoo/tiddlers/monkey"' in html

    tiddler.recipe = 'city'
    html = render(tiddler, {})
    assert 'href="/recipes/city/tiddlers/monkey"' in html

    html = render(tiddler, {'tiddlyweb.config': {'server_prefix': '/wiki'}})
    assert 'href="/wiki/recipes/city/tiddlers/monkey"' in html

