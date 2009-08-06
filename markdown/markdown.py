"""
Render markdown syntax wikitext to HTML
using the markdown2 library.
"""

import markdown2

def render(tiddler, environ):
    """
    Render text in the provided tiddler to HTML.
    """
    return markdown2.markdown(tiddler.text)

