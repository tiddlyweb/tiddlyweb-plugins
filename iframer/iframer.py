"""
Recipe displayer which shows the generated wiki in an iframe.
"""

from tiddlywebplugins.utils import do_html, entitle
from tiddlyweb.web.handler.recipe import _determine_recipe

from jinja2 import Environment, FileSystemLoader
template_env = Environment(loader=FileSystemLoader('templates'))

def init(config):
    config['selector'].add('/iframed/{recipe_name}', GET=iframeit)


@entitle('Recipe')
@do_html()
def iframeit(environ, start_response):
    recipe = _determine_recipe(environ)
    recipe.policy.allows(environ['tiddlyweb.usersign'], 'read')

    template = template_env.get_template('iframer.html')
    return template.generate(recipe=recipe, recipe_list=recipe.get_recipe())
