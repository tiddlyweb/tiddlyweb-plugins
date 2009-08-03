"""
Test the ramstore.
"""
import sys
sys.path.insert(0, '') # need for the Store call below

from tiddlyweb.store import Store
from tiddlyweb.model.bag import Bag

def setup_module(module):
    module.store = Store('ramstore', {})

def test_store_bag():
    bag_in = Bag('bagone')
    bag_in.desc = 'bag description'
    bag_in.policy.read = ['reader']
    bag_in.policy.write = ['writer']

    store.put(bag_in)

    bag_out = store.get(Bag('bagone'))

    assert bag_out.name == bag_in.name

def test_get_bag():
    """
    Make sure we are in a different scope.
    """
    bag_out = store.get(Bag('bagone'))
    assert bag_out.name == 'bagone'
    assert bag_out.desc == 'bag description'
    assert bag_out.policy.read == ['reader']
    assert bag_out.policy.write == ['writer']

def test_list_bags():
    for i in xrange(50):
        store.put(Bag(str(i)))

    bags = store.list_bags()

    assert len(bags) == 51 # bagone is still in there
    assert bags[-2].name == '9' # lexical sort
