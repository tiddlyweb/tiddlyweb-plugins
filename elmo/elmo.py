
from jinja2 import Environment, FileSystemLoader
template_env = Environment(loader=FileSystemLoader('templates'))

from tiddlywebplugins.utils import do_html, entitle

@do_html()
@entitle('elmo!')
def elmo(environ, start_response):
    template = template_env.get_template('elmo.html')
    return template.generate()

def init(config):
    config['selector'].add('/elmo', GET=elmo)
