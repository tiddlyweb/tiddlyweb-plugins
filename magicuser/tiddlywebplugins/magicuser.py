"""
A plugin which provides an extractor for TiddlyWeb.

When a user is extracted, after the normal extraction
has succeeded the user names is looked up as a tiddler
in the bag defined by 'magicuser.bag' in tiddlywebconfig.
The default is 'MAGICUSER'.

That tiddler is then expected for attributes and fields to
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

from tiddlyweb.store import NoTiddlerError
from tiddlyweb.model.tiddler import Tiddler, string_to_tags_list

class Extractor(ExtractorInterface):

    def extract(self, environ, start_response):
        actual_extractors = environ['tiddlyweb.config']['extractors']
        sub_extractors = environ['tiddlyweb.config']['sub_extractors']
        environ['tiddlyweb.config']['extractors'] = sub_extractors

        # XXX this duplicates from tiddlyweb.web.extractor
        userinfo = {"name": u'GUEST', "roles": []}

        candidate_userinfo = _try_extractors(environ, start_response)

        environ['tiddlyweb.config']['extractors'] = actual_extractors

        if candidate_userinfo:
            return self._extract_more_info(environ, candidate_userinfo)
        else:
            return userinfo

    def _extract_more_info(self, environ, userinfo):
        store = environ['tiddlyweb.store'] 
        bag_name = environ['tiddlyweb.config'].get('magicuser.bag', 'MAGICUSER')
        username = userinfo['name']
        tiddler = Tiddler(username, bag_name)
        try:
            tiddler = store.get(tiddler)
        except NoTiddlerError:
            pass # tiddler is empty
        if 'roles' in tiddler.fields:
            userinfo['roles'].extend(string_to_tags_list(tiddler.fields['roles']))
            del tiddler.fields['roles']
        userinfo['fields'] = tiddler.fields
        userinfo['modifier'] = tiddler.modifier
        userinfo['modified'] = tiddler.modified
        userinfo['tags'] = tiddler.tags

        return userinfo


def init(config):
    config['sub_extractors'] = config['extractors']
    config['extractors'] = ['tiddlywebplugins.magicuser']
