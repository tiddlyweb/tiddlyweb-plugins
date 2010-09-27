
from tiddlyweb.config import config
from tiddlywebplugins.utils import get_store
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag
from tiddlywebplugins.hashmaker import init, hash_tiddler_hook

def setup_module(module):
    init(config)
    module.store = get_store(config)

def test_default_hash_generation():
    tiddler1 = Tiddler('hi')
    tiddler1.text = 'hello'

    assert '_hash' not in tiddler1.fields
    hash_tiddler_hook(store.storage, tiddler1)
    assert '_hash' in tiddler1.fields

    tiddler2 = Tiddler('bye')
    tiddler2.text = 'hello'
    hash_tiddler_hook(store.storage, tiddler2)
    assert tiddler1.fields['_hash'] == tiddler2.fields['_hash']

    tiddler2.text = 'goodbye'
    hash_tiddler_hook(store.storage, tiddler2)
    assert tiddler1.fields['_hash'] != tiddler2.fields['_hash']

def test_complex_hash_generation():
    config['hashmaker.attributes'] = ['text', 'karma']

    tiddler1 = Tiddler('hi')
    tiddler1.text = 'hello'
    tiddler1.fields['karma'] = 'bad'
    hash_tiddler_hook(store.storage, tiddler1)

    tiddler2 = Tiddler('bye')
    tiddler2.text = 'hello'
    tiddler2.fields['karma'] = 'bad'
    hash_tiddler_hook(store.storage, tiddler2)

    assert tiddler1.fields['_hash'] == tiddler2.fields['_hash']

    tiddler2.fields['karma'] = 'good'
    hash_tiddler_hook(store.storage, tiddler2)

    assert tiddler1.fields['_hash'] != tiddler2.fields['_hash']

    config['hashmaker.attributes'] = ['text']
    hash_tiddler_hook(store.storage, tiddler1)
    hash_tiddler_hook(store.storage, tiddler2)
    assert tiddler1.fields['_hash'] == tiddler2.fields['_hash']

def test_store_hook():
    bag = Bag('nancy')
    store.put(bag)
    tiddler1 = Tiddler('hi', 'nancy')
    tiddler1.text = 'hello'
    store.put(tiddler1)

    tiddler2 = Tiddler('hi', 'nancy')
    tiddler2 = store.get(tiddler2)

    assert '_hash' in tiddler2.fields

    hash_tiddler_hook(store.storage, tiddler1)
    assert tiddler1.fields['_hash'] == tiddler2.fields['_hash']

# XXX: Validator not tested!
