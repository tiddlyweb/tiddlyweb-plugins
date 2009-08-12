import sys
sys.path.insert(0, '.')
from wikklytextrender import render

from tiddlyweb.model.tiddler import Tiddler


def test_simple_render():
    tiddler = Tiddler('bar')
    tiddler.text = '<html><h1>Hello</h1></html>'
    tiddler.bag = 'zoo'

    html = render(tiddler, {})
    assert html == ''

    html = render(tiddler, {'tiddlyweb.config': {'wikklytext.safe_mode': True}})
    assert html == ''

    html = render(tiddler, {'tiddlyweb.config': {'wikklytext.safe_mode': False}})
    assert html == '<h1>Hello</h1>'

