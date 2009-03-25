
from tiddlyweb.config import config
from tiddlyweb.store import Store
from tiddlyweb.model.bag import Bag

def play():
    store = _store()
    store.list_bags()
    bag = Bag('ahosey')
    bag = store.get(bag)
    tiddlers = bag.list_tiddlers()
    print len(tiddlers) 

    tiddler = store.get(tiddlers[5])
    print tiddler.text


def _store():
    """Get our Store from config."""
    return Store(config['server_store'][0],
            environ={'tiddlyweb.config': config}) 


if __name__ == '__main__':
    play()
