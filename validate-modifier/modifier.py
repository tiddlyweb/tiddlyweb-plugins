"""
A TiddlyWeb plugin which attempts to validate
and or adjust the modifier when a tiddler is PUT.

Don't forget to set the accept policy on the bag that
will use this validator!
"""

import tiddlyweb.web.validator

def validate_modifier(tiddler, environ):
    """
    If the user is anonymous (not authed)
    replace any supplied modifier with 'GUEST'.

    By default the GUEST user means incoming modifier
    will be accepted, any authed user will clobber incoming
    modifier.

    This is _strange_ behavior, so this validator can
    override it.
    """
    username = environ['tiddlyweb.usersign']['name']
    if username == 'GUEST':
        tiddler.modifier = 'GUEST'


tiddlyweb.web.validator.TIDDLER_VALIDATORS.apped(validate_modifier)


def init(config):
    pass
