from tiddlywebplugins.markdown import render
from tiddlyweb.model.tiddler import Tiddler


def test_simple_freelinks():
    tiddler = Tiddler('Foo')
    tiddler.text = 'lorem [[Foo]] ipsum'

    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    output = render(tiddler, environ)

    assert '<a href="Foo">' in output
    assert '>Foo</a>' in output
    assert '[[Foo]]' not in output
    assert output == '<p>lorem <a href="Foo">Foo</a> ipsum</p>'

    tiddler = Tiddler('Foo')
    tiddler.text = 'lorem [[Foo [] Bar]] ipsum'

    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    output = render(tiddler, environ)

    assert '[[Foo [] Bar]]' not in output
    assert '<a href="Foo%20%5B%5D%20Bar">Foo [] Bar</a>' in output
    assert output == '<p>lorem <a href="Foo%20%5B%5D%20Bar">Foo [] Bar</a> ipsum</p>'


def test_labeled_freelinks():
    tiddler = Tiddler('Foo')
    tiddler.text = 'lorem [[hello world|Foo]] ipsum'

    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    output = render(tiddler, environ)

    assert '<a href="Foo">' in output
    assert '>hello world</a>' in output
    assert '[[hello world|Foo]]' not in output
    assert output == '<p>lorem <a href="Foo">hello world</a> ipsum</p>'

    tiddler = Tiddler('Foo')
    tiddler.text = 'lorem [[hello [] world|Foo]] ipsum'

    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    output = render(tiddler, environ)

    assert '[[hello [] world|Foo]]' not in output
    assert '<a href="Foo">hello [] world</a>' in output
    assert output == '<p>lorem <a href="Foo">hello [] world</a> ipsum</p>'


def test_precedence():
    tiddler = Tiddler('Foo')
    tiddler.text = 'lorem [[hello FooBar world]] ipsum'

    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    output = render(tiddler, environ)

    assert '[[hello FooBar world]]' not in output
    assert '<a href="FooBar">FooBar</a>' not in output
    assert '<a href="hello%20FooBar%20world">hello FooBar world</a>' in output
    assert output == '<p>lorem <a href="hello%20FooBar%20world">hello FooBar world</a> ipsum</p>'

    tiddler = Tiddler('Foo')
    tiddler.text = 'lorem [[...|hello FooBar world]] ipsum'

    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    output = render(tiddler, environ)

    assert '[[...|hello FooBar world]]' not in output
    assert '<a href="FooBar">FooBar</a>' not in output
    assert '<a href="hello%20FooBar%20world">...</a>' in output
    assert output == '<p>lorem <a href="hello%20FooBar%20world">...</a> ipsum</p>'
