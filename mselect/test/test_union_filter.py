from tiddlyweb.model.tiddler import Tiddler
from  tiddlywebplugins.mselect import mselect


tiddlers = [Tiddler('1'), Tiddler('c'), Tiddler('a'), Tiddler('b')]

def test_simple_mselect():
    selected_tiddlers = mselect('title:1,title:c', tiddlers)
    assert ['1','c'] == [tiddler.title for tiddler in selected_tiddlers]


def test_mselect_separator():
    selected_tiddlers = mselect('title:1|title:c', tiddlers)
    assert [] == [tiddler.title for tiddler in selected_tiddlers]
    selected_tiddlers = mselect('title:1|title:c', tiddlers, {'tiddlyweb.config':
        {'mselect.separator': '|'}})
    assert ['1','c'] == [tiddler.title for tiddler in selected_tiddlers]
    selected_tiddlers = mselect('title:1,title:c', tiddlers, {'tiddlyweb.config':
        {'mselect.separator': '|'}})
    assert [] == [tiddler.title for tiddler in selected_tiddlers]
