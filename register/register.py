"""
User registration plugin. Essentially all this does is
validate an OpenID and then create a TiddlyWeb user of
that OpenID and assign a Role to it. This allows the system
to go beyond a Policy of 'ANY' to one of 'R:MEMBER', which
is the way to achieve member access to people with openIds
while not allowing _all_ openids.
"""

from jinja2 import Environment, FileSystemLoader
template_env = Environment(loader=FileSystemLoader('templates'))

from tiddlyweb.model.user import User
from tiddlyweb.store import NoUserError
from tiddlyweb.web.wsgi import _challenge_url
from tiddlyweb.web.util import server_base_url
from tiddlywebplugins.utils import do_html, entitle, require_any_user


def init(config):
    config['selector'].add('/register', GET=request, POST=handle)


@do_html()
@entitle('Register')
def request(environ, start_response):
    return _send_start(environ, start_response)


@do_html()
@entitle('Register')
@require_any_user()
def handle(environ, start_response):
    target_role = environ['tiddlyweb.config'].get('register_role', 'MEMBER')
    store = environ['tiddlyweb.store']
    username = environ['tiddlyweb.usersign']['name']
    if _blacklisted(environ, username):
        return _send_start(environ, start_response,
                message='That user has been blocked')
    user = User(username)
    try:
        user = store.get(user)
    except NoUserError:
        pass # is cool if they don't exist yet
    user.add_role('%s' % target_role)
    store.put(user)
    environ['tiddlyweb.usersign'] = {'name': user.usersign,
            'roles': user.list_roles()}
    return _send_finish(environ, start_response)


def _send_finish(environ, start_response):
    template = template_env.get_template('registered.html')
    username = environ['tiddlyweb.usersign']['name']
    return template.generate(username=username,
            home=server_base_url(environ) + '/')
    


def _blacklisted(environ, username):
# XXX this should check a file or something from config
    return username in environ['tiddlyweb.config'].get(
            'register_blacklist', [])


def _send_start(environ, start_response, message=''):
    target_role = environ['tiddlyweb.config'].get('register_role', 'MEMBER')
    template = template_env.get_template('register.html')
    username = environ['tiddlyweb.usersign']['name']
    roles = environ['tiddlyweb.usersign'].get('roles', [])
    return template.generate(message=message, target_role=target_role,
            username=username, roles=roles,
            challenge_url=_challenge_url(environ))
