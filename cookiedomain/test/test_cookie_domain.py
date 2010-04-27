from wsgi_intercept import httplib2_intercept
import wsgi_intercept
import httplib2
import Cookie

from tiddlyweb.store import Store
from tiddlyweb.model.user import User


def setup_module(module):
    from tiddlyweb.config import config
    from tiddlyweb.web import serve
    # we have to have a function that returns the callable,
    # Selector just _is_ the callable
    def app_fn():
        return serve.load_app()
    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('0.0.0.0', 8080, app_fn)
    module.store = Store(config['server_store'][0],
            config['server_store'][1], {'tiddlyweb.config': config})
    user = User('cdent')
    user.set_password('cow')
    module.store.put(user)


def test_check_cookie():
    http = httplib2.Http()
    response, content = http.request(
            'http://0.0.0.0:8080/challenge/cookie_form',
            body='user=%s&password=%s' % ('cdent', 'cow'),
            method='POST',
            headers={'Content-Type': 'application/x-www-form-urlencoded'})
    assert response.previous['status'] == '303'

    user_cookie = response.previous['set-cookie']
    cookie = Cookie.SimpleCookie()
    cookie.load(user_cookie)
    assert 'cdent:' in user_cookie
    assert 'tiddlyweb_user' in user_cookie
    assert 'Domain=0.0.0.0' in user_cookie
