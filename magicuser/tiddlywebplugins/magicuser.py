"""
A plugin which provides an extractor for TiddlyWeb.

When a user is extracted, after the normal extraction
has succeeded the user name is looked up in two ways:

1) In the bag defined by 'magiuser.map' in tiddlywebconfig,
defaulting to 'MAPUSER', look for a tiddler with the title
the same as the username. If the tiddler exists and there
is a field named 'mapped_user', the value of that field
replaces the username extracted.

2) In the bag defined by 'magicuser.bag' in tiddlywebconfig,
defaulting to 'MAGICUSER', look for a tiddler with the title
the same as the username.

That tiddler is then inspected for attributes and fields to
add to the tiddlyweb.usersign dictionary which is passed to
the rest of the TiddlyWeb system (so thus is available to
plugins and the like).

tiddler.fields['roles'] is parsed for roles in the same manner
as the tiddler.tags attribute.

See the test file for examples of how the attributes can be
used.

This plugin works by wrapping the existing extactors configured
for the system. It then calls the wrapped extractors before
doing its own augmentation.
"""
from tiddlyweb.web.extractors import ExtractorInterface
from tiddlyweb.web.extractor import _try_extractors

from tiddlyweb.store import NoTiddlerError, NoBagError
from tiddlyweb.model.tiddler import Tiddler, string_to_tags_list


class Extractor(ExtractorInterface):
    """
    Extract a user information from the HTTP request
    and then add or change the information about the
    user using tiddlers stored in some special bags.
    """

    def extract(self, environ, start_response):
        """
        Extract user information and return a
        dictionary of the information.
        """
        sub_extractors = environ['tiddlyweb.config']['sub_extractors'][:]
        environ['tiddlyweb.config']['extractors'] = sub_extractors

        userinfo = {'name': u'GUEST', 'roles': []}

        candidate_userinfo = _try_extractors(environ, start_response)

        environ['tiddlyweb.config']['extractors'] = ['tiddlywebplugins.magicuser']
        environ['tiddlyweb.config']['sub_extractors'] = sub_extractors

        if candidate_userinfo:
            candidate_userinfo['name'] = self.translate_user(environ,
                    candidate_userinfo['name'])
            return self.extract_more_info(environ, candidate_userinfo)
        else:
            return userinfo

    def translate_user(self, environ, username):
        """
        Translate the currently extracted usersign to a centralized
        name.
        """
        store = environ['tiddlyweb.store']
        bag_name = environ['tiddlyweb.config'].get('magicuser.map', 'MAPUSER')
        tiddler = Tiddler(username, bag_name)
        try:
            tiddler = store.get(tiddler)
        except (NoTiddlerError, NoBagError):
            pass # tiddler is empty
        if 'mapped_user' in tiddler.fields:
            username = tiddler.fields['mapped_user']
        return username

    def extract_more_info(self, environ, userinfo):
        """
        Get more information and attributes about the current
        user from a tiddler named after the user in the bag MAGICUSER.
        """
        store = environ['tiddlyweb.store']
        bag_name = environ['tiddlyweb.config'].get('magicuser.bag',
                'MAGICUSER')
        username = userinfo['name']
        tiddler = Tiddler(username, bag_name)
        try:
            tiddler = store.get(tiddler)
        except (NoTiddlerError, NoBagError):
            pass # tiddler is empty
        if 'roles' in tiddler.fields:
            userinfo['roles'].extend(string_to_tags_list(
                tiddler.fields['roles']))
            del tiddler.fields['roles']
        userinfo['fields'] = tiddler.fields
        userinfo['modifier'] = tiddler.modifier
        userinfo['modified'] = tiddler.modified
        userinfo['tags'] = tiddler.tags

        return userinfo


def init(config):
    """
    Initialize the plugin by changing configuration.
    """
    if 'tiddlywebplugins.magicuser' not in config['extractors']:
        config['sub_extractors'] = config['extractors']
        config['extractors'] = ['tiddlywebplugins.magicuser']
