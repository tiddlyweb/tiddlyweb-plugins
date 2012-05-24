from tiddlywebplugins.markdown import render
from tiddlyweb.model.tiddler import Tiddler


def test_urlification():
    tiddler = Tiddler('blah')
    tiddler.text = """
            lorem ipsum http://example.org dolor sit amet
            ... http://www.example.com/foo/bar ...
     """

    environ = {}
    output = render(tiddler, environ)

    for url in ["http://example.org", "http://www.example.com/foo/bar"]:
        assert '<a href="%(url)s">%(url)s</a>' % { "url": url } in output
