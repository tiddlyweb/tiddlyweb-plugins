

import urllib

from tiddlyweb.web.sendtiddlers import send_tiddlers
from tiddlyweb.model.bag import Bag
from tiddlyweb import control

def init(config_in):
    config_in['selector'].add('/bags/{bag_name}/tags', GET=list_tags)
    config_in['selector'].add('/bags/{bag_name}/tags/{tag_name}', GET=get_tag)
    config_in['selector'].add('/bags/{bag_name}/tags/{tag_name}/tiddlers', GET=tagged_tiddlers)


def list_tags(environ, start_response):
    store = environ['tiddlyweb.store']
    bag_name = unicode(urllib.unquote(environ['wsgiorg.routing_args'][1]['bag_name']), 'utf-8')
    tag_names = _tags_for_bag(store.get(Bag(bag_name)))

    start_response('200 OK', [
        ('Content-Type', 'text/plain')
        ])
    return ('%s\n' % tag for tag in tag_names)

def _tags_for_bag(bag):
    tiddlers = control.get_tiddlers_from_bag(bag)
    tags = set()
    for tiddler in tiddlers:
        tags.update(set(tiddler.tags))
    return tags


def get_tag(environ, start_response):
    tag_name = unicode(urllib.unquote(environ['wsgiorg.routing_args'][1]['tag_name']), 'utf-8')
    start_response('200 OK', [
        ('Content-Type', 'text/plain')
        ])
    return ['i am tag %s' % tag_name]


def tagged_tiddlers(environ, start_response):
    store = environ['tiddlyweb.store']
    bag_name = unicode(urllib.unquote(environ['wsgiorg.routing_args'][1]['bag_name']), 'utf-8')
    tag_name = unicode(urllib.unquote(environ['wsgiorg.routing_args'][1]['tag_name']), 'utf-8')
    bag = store.get(Bag(bag_name))
    tmp_bag = Bag('tmpbag', tmpbag=True)
    tmp_bag.add_tiddlers(control.filter_tiddlers_from_bag(bag, 'select=tag:%s' % tag_name))

    return send_tiddlers(environ, start_response, tmp_bag)
