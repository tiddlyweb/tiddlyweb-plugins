"""
Drive a home page from within TiddlyWiki.
"""

from jinja2 import Environment, FileSystemLoader
template_env = Environment(loader=FileSystemLoader('templates'))

from tiddlyweb.web.wsgi import HTMLPresenter

def home(environ, start_response):
    template = template_env.get_template('home.html')
    environ['tiddlyweb.title'] = environ['tiddlyweb.config']['hometitle']
    roles = environ['tiddlyweb.usersign'].get('roles', [])
    admin = 'ADMIN' in roles
    start_response('200 OK', [('Content-Type', 'text/html')])
    return template.generate(
            user=environ['tiddlyweb.usersign']['name'],
            admin=admin
            )

def replace_handler(selector, path, new_handler):
    for index, (regex, handler) in enumerate(selector.mappings):
        if regex.match(path) is not None:
            selector.mappings[index] = (regex, new_handler)


def header_extra(self, environ):
    return '<span id="homer" style="float:right"><a href="/">Home</a></span>'


HTMLPresenter.header_extra = header_extra


def init(config):
    replace_handler(config['selector'], '/', dict(GET=home))
