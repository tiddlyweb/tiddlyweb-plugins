"""
A plugin that allows for the listing, updating and
creation of TiddlyWeb users over HTTP. It is called
socialusers because anyone can create a new user, and
any existing user can list all the users. This is
extremely insecure for some settings, and perfectly
okay for others. You need to be the judge.

This module provides very functionality which
will expand to optionally interoperate with the
tiddlywebplugins.magicuser extractor, which uses
additional user data stored in tiddlers.
"""

import simplejson
import urllib

from tiddlyweb.web.http import HTTP404, HTTP415, HTTP400, HTTP409, HTTP403
from tiddlyweb.model.user import User
from tiddlyweb.store import NoUserError

from tiddlywebplugins.utils import require_any_user


def init(config):
    if 'selector' in config:
        config['selector'].add('/users', GET=list_users, POST=post_user)
        config['selector'].add('/users/{usersign}', GET=get_user, PUT=put_user)


@require_any_user()
def list_users(environ, start_response):
    """
    List all the users on the system by name, text/plain,
    one user per line.
    The request must be made by an existing and logged in user.
    """
    store = environ['tiddlyweb.store']
    users = store.list_users()
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ('%s\n' % user.usersign for user in users)


@require_any_user()
def get_user(environ, start_response):
    """
    Get information about the user named in the request.
    Right now this just returns the username, acknowledging
    the user exists.
    The request must be made by an existing and logged in user.
    """
    store = environ['tiddlyweb.store']
    try:
        usersign = environ['wsgiorg.routing_args'][1]['usersign']
        user = User(usersign)
        user = store.get(user)
    except (NoUserError, KeyError), exc:
        raise HTTP404('Unable to load user: %s, %s' % (usersign, exc))
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ['%s' % user.usersign]


def put_user(environ, start_response):
    """
    Allow a user or an admin to set the password for a user
    at /users/{usersign}. A non-admin can only set their
    own password.

    The sent data is a JSON dict with at least the key
    'password' with a value of whatever the password
    should be.

    Users of this method should take not that that password
    is being sent in the clear over what is likely an
    unencrypted network.
    """
    store = environ['tiddlyweb.store']
    current_user = environ['tiddlyweb.usersign']
    target_user = environ['wsgiorg.routing_args'][1]['usersign']
    target_user = urllib.unquote(target_user)
    target_user = unicode(target_user, 'utf-8')

    if not ('ADMIN' in current_user['roles'] or
            current_user['name'] == target_user):
        raise HTTP403('Incorrect User')

    content_type = environ['tiddlyweb.type']
    length = environ['CONTENT_LENGTH']
    if content_type != 'application/json':
        raise HTTP415('application/json required')
    content = environ['wsgi.input'].read(int(length))

    try:
        user_info = simplejson.loads(content)
    except ValueError, exc:
        raise HTTP400('Invalid JSON, %s' % exc)

    try:
        user = User(target_user)
        try:
            store.get(user)
        except NoUserError:
            raise HTTP404()
        user.set_password(user_info['password'])
    except KeyError, exc:
        raise HTTP400('Missing required data: %s', exc)

    store.put(user)
    start_response('204 No Content', [
        ('Content-Type', 'text/html; charset=UTF-8')
        ])
    return ['Updated %s' % target_user]


def post_user(environ, start_response):
    """
    Create a new user through a JSON POST to /users.
    If the not JSON, return 415. If users exists, return 409.

    The JSON should be a dict with two keys: 'username'
    and 'password'. Future iterations of this code
    will take additional keys and save them as fields
    to be used with the tiddlywebplugins.magicuser
    extractor.
    """
    content_type = environ['tiddlyweb.type']
    if content_type != 'application/json':
        raise HTTP415('application/json required')
    length = environ['CONTENT_LENGTH']
    content = environ['wsgi.input'].read(int(length))
    store = environ['tiddlyweb.store']

    try:
        user_info = simplejson.loads(content)
    except ValueError, exc:
        raise HTTP400('Invalid JSON, %s' % exc)

    try:
        user = User(user_info['username'])
        try:
            store.get(user)
            raise HTTP409('User exists')
        except NoUserError:
            pass # we're carrying on below
        user.set_password(user_info['password'])
    except KeyError, exc:
        raise HTTP400('Missing required data: %s', exc)

    store.put(user)

    start_response('201 Created', [
        ('Content-Type', 'text/html; charset=UTF-8')
        ])
    return ['Created %s' % user_info['username']]
