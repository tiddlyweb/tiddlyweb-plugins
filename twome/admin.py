"""
An admin tool for TiddlyWiki.

These decorators could just as
easily be middleware, but exploring this
option for now. These could probably
be useful stuck into a tiddlyweb.plugin
library. Shit, more framework!
"""

from tiddlyweb.model.policy import UserRequiredError
from tiddlyweb.model.user import User

from jinja2 import Environment, FileSystemLoader
template_env = Environment(loader=FileSystemLoader('templates'))

from twplugins import do_html, require_role, entitle


@do_html()
@require_role('ADMIN')
@entitle('Main Admin')
def admin(environ, start_respons):
    template = template_env.get_template('admin.html')
    return template.generate()


@do_html()
@require_role('ADMIN')
@entitle('Recipes Admin')
def recipes(environ, start_respons):
    store = environ['tiddlyweb.store']
    recipes = store.list_recipes()
    template = template_env.get_template('recipes.html')
    return template.generate(
            recipes=recipes
            )


@do_html()
@require_role('ADMIN')
@entitle('Bags Admin')
def bags(environ, start_respons):
    store = environ['tiddlyweb.store']
    bags = store.list_bags()
    template = template_env.get_template('bags.html')
    return template.generate(
            bags=bags
            )


@do_html()
@require_role('ADMIN')
@entitle('Users Admin')
def users(environ, start_respons):
    store = environ['tiddlyweb.store']
    #users = store.list_users()
    users = [User(name) for name in ['cdent','foobar']]
    template = template_env.get_template('users.html')
    return template.generate(
            users=users
            )


def init(config):
    config['selector'].add('/admin', GET=admin)
    config['selector'].add('/admin/recipes', GET=recipes)
    config['selector'].add('/admin/bags', GET=bags)
    config['selector'].add('/admin/users', GET=users)
