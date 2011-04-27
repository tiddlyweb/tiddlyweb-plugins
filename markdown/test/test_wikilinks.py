from tiddlywebplugins.markdown import render
from tiddlyweb.model.tiddler import Tiddler


sample = """# Hello
    
This is WikiLink

* List
* List
"""

sample_linked = """

This is WikiLink and this is not: [NotLink](http://example.com).

This forthcoming in camel case but actually
a link [label](http://example.org/CamelCase)

"""


def test_no_wiki():
    tiddler = Tiddler('hello')
    tiddler.text = sample

    environ = {}
    output = render(tiddler, environ)
    assert '<h1>' in output
    assert '<li>' in output
    assert 'href' not in output

    environ = {'tiddlyweb.config': {'markdown.wiki_link_base': ''}}
    output = render(tiddler, environ)
    assert 'href' in output
    assert '<a href="WikiLink">' in output
    assert '>WikiLink</a>' in output

    tiddler.text = sample_linked
    output = render(tiddler, environ)
    assert '"NotLink"' not in output
    assert '<a href="http://example.org/CamelCase">label</a>' in output
