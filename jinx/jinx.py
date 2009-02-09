
from jinja2 import Environment, FileSystemLoader
template_env = Environment(loader=FileSystemLoader('templates'))

from twplugins import do_html, entitle, require_any_user

@do_html()
@entitle('Hello World')
@require_any_user()
def jinx(environ, start_response):
    username = environ['tiddlyweb.usersign']['name']
    message = environ['wsgiorg.routing_args'][1]['message']
    if not message:
        message = 'Hello'
    store = environ['tiddlyweb.store']
    bags = store.list_bags()
    template = template_env.get_template('jinx.html')
    return template.generate(message=message, name=username, bags=bags)


def init(config):
    config['selector'].add('/jinx[/{message:segment}]', GET=jinx)
