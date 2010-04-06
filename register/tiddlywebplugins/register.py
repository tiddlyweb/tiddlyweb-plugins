"""
A user registration plugin for TiddlyWeb.

What this does is validate an OpenID and then create a
TiddlyWeb user of that OpenID and assign a Role to it.
This allows the system to go beyond a Policy of 'ANY'
to one of 'R:MEMBER'. This is a way to provide member
access to people with openIds while not allowing all
openids.

It uses a few optional configuration settings:

    register.role: The role assigned to newly registered
        users. Defaults to "MEMBER".
    register.start_href: The link to send users to after
        they have registered. Defaults to "/".
    register.start_title: The title of the link. Defaults
        to "Get Started".
    register.blacklist: A list of openids to never allow
        to register. Defaults to an empty list.

Because tiddlywebplugins.templates is being used, the 
register.html and registered.html templates may be overriden
per instance by creating a templates directory in the instance
directory and putting new versions of the templates in there.
"""

from tiddlyweb.model.user import User
from tiddlyweb.store import NoUserError
from tiddlyweb.web.wsgi import _challenge_url
from tiddlyweb.web.util import server_base_url
from tiddlywebplugins.utils import do_html, entitle, require_any_user
from tiddlywebplugins.templates import get_template


def init(config):
    """
    Add the /register route.
    """
    if 'selector' in config:
        config['selector'].add('/register', GET=request, POST=handle)


@do_html()
@entitle('Register')
def request(environ, start_response):
    """
    Send the initial page.
    """
    return _send_start(environ, start_response)


@do_html()
@entitle('Register')
@require_any_user()
def handle(environ, start_response):
    """
    Handle a posted request for registration.

    If the provided username is blacklisted, ask them to
    log in as someone else. Otherwise send closing
    material with a link to get started.
    """
    pretty_name = environ['tiddlyweb.query'].get('pretty_name', [None])[0]
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
    if pretty_name:
        user.note = pretty_name
    store.put(user)
    environ['tiddlyweb.usersign'] = {'name': user.usersign,
            'roles': user.list_roles()}
    return _send_finish(environ, start_response)


def _send_finish(environ, start_response):
    template = get_template(environ, 'registered.html')
    username = environ['tiddlyweb.usersign']['name']
    start = {
            'href': environ['tiddlyweb.config'].get('register.start_href', '/'),
            'title': environ['tiddlyweb.config'].get('register.start_title', 'Get Started'),
            }
    return template.generate(start=start, username=username,
            home=server_base_url(environ) + '/')


def _blacklisted(environ, username):
    return username in environ['tiddlyweb.config'].get(
            'register.blacklist', [])


def _send_start(environ, start_response, message=''):
    target_role = environ['tiddlyweb.config'].get('register.role', 'MEMBER')
    template = get_template(environ, 'register.html')
    username = environ['tiddlyweb.usersign']['name']
    roles = environ['tiddlyweb.usersign'].get('roles', [])
    return template.generate(message=message, target_role=target_role,
            username=username, roles=roles,
            challenge_url=_challenge_url(environ))
