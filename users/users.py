"""
A plugin that allows for the administration of
users over HTTP. This is done as a plugin for two
reasons:

    * To make use of it easily optional for any installation.
    * To allow exploration of the API before possibly solidifying
      it in the core.

Basically it allows an admin user to view all the users and
make changes.

Add 'users' to system_plugins. To view any of these urls
a user with the ADMIN will need to exist in the store.
"""

from tiddlywebplugins.utils import require_role
from tiddlyweb.web.http import HTTP404
from tiddlyweb.model.user import User
from tiddlyweb.store import NoUserError

@require_role('ADMIN')
def list_users(environ, start_response):
    store = environ['tiddlyweb.store']
    users = store.list_users()
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ['%s\n' % user for user in users]


@require_role('ADMIN')
def get_user(environ, start_response):
    store = environ['tiddlyweb.store']
    try:
        usersign = environ['wsgiorg.routing_args'][1]['usersign']
        user = User(usersign)
        user = store.get(user)
    except (NoUserError, KeyError), exc:
        raise HTTP404('Unable to load user: %s, %s' % (usersign, exc))
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ['%s' % user]


@require_role('ADMIN')
def put_user(environ, start_response):
    store = environ['tiddlyweb.store']
    pass


def init(config):
    config['selector'].add('/users', GET=list_users)
    config['selector'].add('/users/{usersign}', GET=get_user, PUT=put_user)
