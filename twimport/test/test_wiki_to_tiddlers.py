"""
test importing a wiki.
"""

WIKI_HTML_FILE = 'test/samples/tiddlers.html'
WIKI_WIKI_FILE = 'test/samples/tiddlers.wiki'

from tiddlywebplugins.twimport import wiki_to_tiddlers


def test_wiki_wiki_to_tiddlers():
    tiddlers = wiki_to_tiddlers(WIKI_WIKI_FILE)

    assert len(tiddlers) == 9 # shadow?
    
    titles = [tiddler.title for tiddler in tiddlers]
    assert 'oog' in titles
    assert 'codeblocked' in titles

def test_wiki_html_to_tiddlers():
    tiddlers = wiki_to_tiddlers(WIKI_HTML_FILE)

    assert len(tiddlers) == 9 # shadow?
    
    titles = [tiddler.title for tiddler in tiddlers]
    assert 'oog' in titles
    assert 'codeblocked' in titles
