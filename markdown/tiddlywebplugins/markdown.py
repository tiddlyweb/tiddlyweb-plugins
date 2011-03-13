"""
Render markdown syntax wikitext to HTML
using the markdown2 library.

If 'markdown.wiki_link_base' is set in config,
then CamelCase words will becomes links, prefix
by wiki_link_base. Set it to '' to activate WikiLinks
without any prefix.

To use on Tiddlers which have a type of 'text/x-markdown'
adjust config to include:

 'wikitext.type_render_map' :{
     'text/x-markdown': 'tiddlywebplugins.markdown'
     }

If you want all text tiddlers to be rendered as markdown,
then set

 'wikitext.default_renderer': 'tiddlywebplugins.markdown'
"""

import re
import markdown2


PATTERNS = {
    'wikilink': re.compile(r'(\b[A-Z][a-z]+[A-Z]\w+\b)')
}


class WikiLinker(object):

    def __init__(self, base):
        self.base = base

    def __call__(self, match):
        return self.base + match.group()


def render(tiddler, environ):
    """
    Render text in the provided tiddler to HTML.
    """
    wiki_link_base = environ.get('tiddlyweb.config', {}).get(
            'markdown.wiki_link_base', None)
    if wiki_link_base is not None:
        link_patterns = [
            # Match a wiki page link LikeThis.
            (PATTERNS['wikilink'], WikiLinker(wiki_link_base))
        ]
    else:
        link_patterns = []
    processor = markdown2.Markdown(extras=['link-patterns'],
                               link_patterns=link_patterns)
    return processor.convert(tiddler.text)
