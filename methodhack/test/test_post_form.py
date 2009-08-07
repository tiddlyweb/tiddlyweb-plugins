"""
mahemoff identified a problem with methodhack
when dealing with form encoded input coming in
on a POST attempting to a be a PUT. The system
tries to read wsgi.input twice and hangs. 

By moving methodhack before Query, this should
fix it. But we'll see.

This test isn't really a test, it is a bug replication.
"""

import sys
sys.path.insert(0, '')

from wsgi_intercept import httplib2_intercept
import wsgi_intercept
import httplib2

from tiddlyweb.config import config
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import Store


def setup_module(module):
    config['system_plugins'] = ['methodhack']
    from tiddlyweb.web import serve
    def app_fn():
        return serve.load_app()
    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('our_test_domain', 8001, app_fn) 
    module.store = Store(config['server_store'][0], {'tiddlyweb.config': config})


def test_post_a_form_put():
    store.put(Bag('foo'))
    content = 'name=News&resources=http%3A%2F%2Fbbc.co.uk%0D%0Ahttp%3A%2F%2Fnews.google.com%0D%0Ahttp%3A%2F%2Fmemeorandum.com%0D%0A%0D%0A'
    http = httplib2.Http()
    response, output = http.request('http://our_test_domain:8001/bags/foo/tiddlers/bar?http_method=PUT',
            method='POST', headers={'Content-Type': 'application/x-www-form-urlencoded'},
            body=content)

    assert response['status'] == '204'
    tiddler = store.get(Tiddler('bar', 'foo'))
    assert tiddler.text == content

