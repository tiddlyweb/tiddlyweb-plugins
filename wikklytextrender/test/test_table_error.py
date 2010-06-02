

from tiddlywebplugins.wikklytextrender import render
from tiddlyweb.model.tiddler import Tiddler


def test_simple_render():
    tiddler = Tiddler('bar')
    tiddler.text = """
|hello|goodbye|h
|foo|bar|
"""
    tiddler.bag = 'zoo'

    html = render(tiddler, {})
    assert 'WikError' in html

