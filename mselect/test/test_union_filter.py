from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.config import config
from tiddlywebplugins.mselect import init


tiddlers = [Tiddler('1'), Tiddler('c'), Tiddler('a'), Tiddler('b')]

def setup_module(module):
    init(config)
    from tiddlywebplugins.mselect import test_mselect as tm
    module.test_mselect = tm

def test_simple_mselect():
    selected_tiddlers = test_mselect('title:1,title:c', tiddlers)
    assert ['1','c'] == [tiddler.title for tiddler in selected_tiddlers]


def test_mselect_separator():
    selected_tiddlers = test_mselect('title:1|title:c', tiddlers)
    assert [] == [tiddler.title for tiddler in selected_tiddlers]
    selected_tiddlers = test_mselect('title:1|title:c', tiddlers, {'tiddlyweb.config':
        {'mselect.separator': '|'}})
    assert ['1','c'] == [tiddler.title for tiddler in selected_tiddlers]
    selected_tiddlers = test_mselect('title:1,title:c', tiddlers, {'tiddlyweb.config':
        {'mselect.separator': '|'}})
    assert [] == [tiddler.title for tiddler in selected_tiddlers]
