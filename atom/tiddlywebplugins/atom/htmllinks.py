"""
Add <link> elements for Atom feeds to tiddler collections.
"""

from tiddlyweb.serializations import SerializationInterface
from tiddlyweb.serializations.html import Serialization as HTMLSerialization
from tiddlyweb.web.util import tiddler_url

class Serialization(HTMLSerialization):

    def _tiddler_list_header(self, wiki_link):
        if wiki_link:
            self.environ['tiddlyweb.links'].append(
                    '<link rel="alternate" type="application/atom+xml" title="Atom" href="%s" />' \
                            % '%s.atom' % wiki_link
                    )
        return HTMLSerialization._tiddler_list_header(self, wiki_link)

    def tiddler_as(self, tiddler):
        self.environ['tiddlyweb.links'].append(
                    '<link rel="alternate" type="application/atom+xml" title="Atom" href="%s" />' \
                            % '%s.atom' % tiddler_url(self.environ, tiddler)
                            )
        return HTMLSerialization.tiddler_as(self, tiddler)



