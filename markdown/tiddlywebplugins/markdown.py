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
    'freelink': re.compile(r'\[\[(.+?)\]\]'), # XXX: should be surrounded by \b
    'wikilink': re.compile(r'((?<=\s)[A-Z][a-z]+[A-Z]\w+\b)')
}


class FreeLinker(object):

    def __init__(self, base):
        self.base = base

    def __call__(self, match):
        link = match.groups()[0]
        try:
            label, page = link.split("|", 1)
        except ValueError: # no label
            label = page = link
        return (page, label)


# subclass original Markdown class to allow for custom link labels
# XXX: patch pending: https://github.com/trentm/python-markdown2/pull/53
g_escape_table = markdown2.g_escape_table
_hash_text = markdown2._hash_text
class Markdown(markdown2.Markdown):

    def _do_link_patterns(self, text):
        link_from_hash = {}
        for regex, repl in self.link_patterns:
            replacements = []
            for match in regex.finditer(text):
                title = None # XXX: rename variable (ambiguous/misleading)
                if hasattr(repl, "__call__"):
                    components = repl(match) # XXX: rename variable
                    try:
                        href, title = components
                    except ValueError:
                        href = components
                else:
                    href = match.expand(repl)
                replacements.append((match.span(), href, title))
            for (start, end), href, title in reversed(replacements):
                escaped_href = (
                    href.replace('"', '&quot;')  # b/c of attr quote
                        # To avoid markdown <em> and <strong>:
                        .replace('*', g_escape_table['*'])
                        .replace('_', g_escape_table['_']))
                if not title:
                    title = text[start:end]
                link = '<a href="%s">%s</a>' % (escaped_href, title)
                hash = _hash_text(link)
                link_from_hash[hash] = link
                text = text[:start] + hash + text[end:]
        for hash, link in link_from_hash.items():
            text = text.replace(hash, link)
        return text


def render(tiddler, environ):
    """
    Render text in the provided tiddler to HTML.
    """
    wiki_link_base = environ.get('tiddlyweb.config', {}).get(
            'markdown.wiki_link_base', None)
    if wiki_link_base is not None:
        link_patterns = [
            (PATTERNS['freelink'], FreeLinker(wiki_link_base)),
            (PATTERNS['wikilink'], r"\1")
        ]
    else:
        link_patterns = []
    processor = Markdown(extras=['link-patterns'],
            link_patterns=link_patterns)
    return processor.convert(tiddler.text)
