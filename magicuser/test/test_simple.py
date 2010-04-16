
import shutil

from tiddlyweb.store import Store
from tiddlyweb.config import config

from tiddlywebplugins.magicuser import Extractor

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag


def setup_module(module):
    clean_store()
    module.environ = {'tiddlyweb.config': config}
    module.store = Store(config['server_store'][0], config['server_store'][1], module.environ)
    module.environ['tiddlyweb.store'] = module.store


def clean_store():
    try:
        shutil.rmtree('store')
    except:
        pass # !


def test_simple_magic():
    bag = Bag('MAGICUSER')
    store.put(bag)
    extractor = Extractor()
    userinfo = {'name': 'cdent', 'roles': ['HELLO']}

    more_info = extractor.extract_more_info(environ, userinfo)

    assert 'modifier' in more_info
    assert 'name' in more_info
    assert 'roles' in more_info
    assert 'tags' in more_info
    assert 'fields' in more_info
    assert 'modified' in more_info

    assert more_info['tags'] == []
    assert more_info['fields'] == {}
    assert more_info['roles'] == ['HELLO']

    tiddler = Tiddler('cdent', 'MAGICUSER')
    tiddler.fields['roles'] = "GOODBYE CHRISTMAS EASTER ADMIN"
    tiddler.tags = ['monkey', 'hello', 'barney']
    tiddler.fields['spaces'] = "one two three"
    store.put(tiddler)

    more_info = extractor.extract_more_info(environ, userinfo)

    assert more_info['tags'] == ['monkey', 'hello', 'barney']
    assert len(more_info['roles']) == 5
    for role in ['HELLO', 'GOODBYE', 'CHRISTMAS', 'EASTER', 'ADMIN']:
        assert role in more_info['roles']
    assert more_info['fields']['spaces'] == 'one two three'


def test_simple_translate():
    bag = Bag('MAPUSER')
    store.put(bag)
    tiddler = Tiddler('xfoo.example.com', 'MAPUSER')
    tiddler.fields['mapped_user'] = 'xfoo'
    store.put(tiddler)

    extractor = Extractor()

    assert extractor.translate_user(environ, 'xfoo.example.com') == 'xfoo'
