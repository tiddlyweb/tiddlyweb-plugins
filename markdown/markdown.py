"""
Render markdown syntax wikitext to HTML
using the markdown2 library.
"""

import re
import markdown2

class WikiLinker(object):

    def __init__(self, base):
        self.base = base

    def __call__(self, match):
        return self.base + match.group()


def render(tiddler, environ):
    """
    Render text in the provided tiddler to HTML.
    """
    wiki_link_base = environ.get('markdown.wiki_link_base', None)
    if wiki_link_base:
        link_patterns = [
            # Match a wiki page link LikeThis.
            (re.compile(r"(\b[A-Z][a-z]+[A-Z]\w+\b)"), WikiLinker(wiki_link_base))
        ]
    else:
        link_patterns = []
    processor = markdown2.Markdown(extras=["link-patterns"],
                               link_patterns=link_patterns)
    return processor.convert(tiddler.text)

