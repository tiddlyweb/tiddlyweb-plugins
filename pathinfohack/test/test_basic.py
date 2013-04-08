
from tiddlywebplugins.pathinfohack import PathInfoHack

def start_response(*args):
    pass

def app(environ, start_response):
    return []

def test_basic_clean():
    environ = {
            'REQUEST_URI': '/bags/cdent/tiddlers/monkey',
            'PATH_INFO': '/bags/cdent/tiddlers/monkey',
            }
    PathInfoHack(app)(environ, start_response)
    assert environ['PATH_INFO'] == '/bags/cdent/tiddlers/monkey'

def test_no_script():
    environ = {
            'REQUEST_URI': '/bags/cdent/tiddlers/monkey%2fcow',
            'PATH_INFO': '/bags/cdent/tiddlers/monkey/cow',
            }
    PathInfoHack(app)(environ, start_response)
    assert environ['PATH_INFO'] == '/bags/cdent/tiddlers/monkey%2fcow'

def test_script():
    environ = {
            'REQUEST_URI': '/wiki/bags/cdent/tiddlers/monkey%2fcow',
            'PATH_INFO': '/bags/cdent/tiddlers/monkey/cow',
            'SCRIPT_NAME': '/wiki'
            }
    PathInfoHack(app)(environ, start_response)
    assert environ['PATH_INFO'] == '/bags/cdent/tiddlers/monkey%2fcow'
