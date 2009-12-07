"""
Test that the disting actually dists.

This is obviously incomplete, but at leasts adds a
bit of coverage.
"""

import os
import shutil


from tiddlyweb.model.bag import Bag
from tiddlyweb.store import Store

SAMPLE_CONFIG = {
        'server_store': ['tiddlywebplugins.diststore', {
            'main': ['text', {'store_root': 'store1'}],
            'extras': [
                (r'^c', ['text', {'store_root': 'store2'}]),
                    ],
                }],
        }
ENVIRON = {'tiddlyweb.config': SAMPLE_CONFIG}


def setup_module(module):
    for dir in ['store1', 'store2']:
        if os.path.exists(dir):
            shutil.rmtree(dir)


def test_where_it_goes():
    store = Store('tiddlywebplugins.diststore', environ=ENVIRON)
    bbag = Bag('bbag')
    cbag = Bag('cbag')
    store.put(bbag)
    store.put(cbag)

    assert os.path.exists('store1/bags/bbag/tiddlers')
    assert os.path.exists('store2/bags/cbag/tiddlers')
    assert not os.path.exists('store2/bags/bbag/tiddlers')
    assert not os.path.exists('store1/bags/cbag/tiddlers')
