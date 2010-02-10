import tiddlywebplugins.virtualhosting
from tiddlyweb.web.util import server_host_url

from tiddlyweb.config import config

def test_http_host():
    environ = {
            'tiddlyweb.config': config,
            }
    url = server_host_url(environ)
    assert url == 'http://0.0.0.0:8080'

    environ['HTTP_HOST'] = 'fancy.virtual.domain:9090'
    environ['wsgi.url_scheme'] = 'https'
    url = server_host_url(environ)
    assert url == 'https://fancy.virtual.domain:9090'



