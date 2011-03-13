from tiddlywebplugins.markdown import render
from tiddlyweb.model.tiddler import Tiddler


def test_simple_spacelinks():
    tiddler = Tiddler('Foo')
    tiddler.text = 'lorem [[Foo]]@alpha ipsum'

    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    output = render(tiddler, environ)

    assert '[[Foo]]@alpha' not in output
    assert output.startswith('lorem <a href="')
    assert output.endswith('/Foo">Foo</a> ipsum')
    # TODO: test space URI


def test_labeled_spacelinks():
    tiddler = Tiddler('Foo')
    tiddler.text = 'lorem [[hello world|Foo]]@alpha ipsum'

    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    output = render(tiddler, environ)

    assert '[[hello world|Foo]]@alpha' not in output
    assert output.startswith('lorem <a href="')
    assert output.endswith('/Foo">hello world</a> ipsum')
    # TODO: test space URI
