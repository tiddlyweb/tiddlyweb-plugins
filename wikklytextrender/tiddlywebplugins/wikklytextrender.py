"""
A TiddlyWiki wiki syntax to HTML renderer for use with 
TiddlyWeb. Rendering is done using wikklytext.

To use add one or both of the following to tiddlywebconfig.py:

    wikitext.default_renderer': 'wikklytextrender',
    'wikitext.default_render_map': {
        'text/x-tiddlywiki': 'wikklytextrender',
    },

If 'wikklytext.safe_mode' is set to False, HTML within tiddler.text
that is wrapped in <html> tags will be preserved. If True, the HTML 
is removed. True is the default.

If 'wikklytext.plugin-dir' is set to a path, that path is used as
a container of plugins used by WikklyText.

If 'wikklytext.use_wikiwords' is set to False, then CamelCase style
wikiwords are not rendered. The default is True.
"""

import wikklytext
import urllib

from tiddlyweb.web.util import encode_name


def render(tiddler, environ):
    """
    Render TiddlyWiki wikitext in the provided
    tiddler to HTML. The provided path helps
    set paths in wikilinks correctly.
    """
    server_prefix = environ.get('tiddlyweb.config',
            {}).get('server_prefix', '')
    if tiddler.recipe:
        path = 'recipes/%s/tiddlers' % encode_name(tiddler.recipe)
    elif tiddler.bag:
        path = 'bags/%s/tiddlers' % encode_name(tiddler.bag)
    else:
        path = ''
    html = wikitext_to_wikklyhtml('%s/' % server_prefix,
            path, tiddler, environ)
    return unicode(html, 'utf-8')


def wikitext_to_wikklyhtml(base_url, path_url, tiddler, environ):
    """
    Turn a wikitext into HTML.
    base_url: starting url for links in the wikitext (e.g. '/')
    path_url: path from base to wikitext (e.g. 'recipes/foorecipe/tiddlers')
    """

    def our_resolver(url_fragment, base_url, site_url):
        """
        Turn url information for a wikiword into a link.
        """
        if '://' in url_fragment or url_fragment.startswith('/'):
            return url_fragment, True
        return '%s%s' % (base_url, urllib.quote(url_fragment, safe='')), False


    safe_mode_setting = environ.get('tiddlyweb.config', {}).get(
            'wikklytext.safe_mode', True)
    plugindir = environ.get('tiddlyweb.config', {}).get(
            'wikklytext.plugin-dir', '')
    use_wikiwords = environ.get('tiddlyweb.config', {}).get(
            'wikklytext.use_wikiwords', True)

    posthook = PostHook(use_wikiwords)

    link_context = {
            '$BASE_URL': '%s%s' % (base_url, path_url),
            '$REFLOW': 0}

    try:
        context = wikklytext.WikContext(plugin_dirs=plugindir,
                url_resolver=our_resolver)
        context.environ = environ
        context.tiddler = tiddler
        html, newcontext = wikklytext.WikklyText_to_InnerHTML(
                text=tiddler.text,
                context=context,
                setvars=link_context,
                encoding='utf-8',
                safe_mode=safe_mode_setting,
                url_resolver=our_resolver,
                tree_posthook=posthook.treehook)
    except wikklytext.WikError, exc:
        html = '<pre>Unable to render wikitext: %s</pre>' % exc
    return html


class PostHook(object):
    """
    After we transform the wikitext into a
    tree with need to link up the wiki words.
    """

    def __init__(self, use_wikiwords=True):
        # make map of wikiwords
        self.wikiwords = InfiniteDict()
        self.use_wikiwords = use_wikiwords

    def treehook(self, rootnode, context):
        """
        Turn wikiwords into links.
        """
        if self.use_wikiwords:
            from wikklytext.wikwords import wikiwordify
            # add links to any wikiword
            wikiwordify(rootnode, context, self.wikiwords)
        else:
            pass


class InfiniteDict(dict):
    """
    Model a dictionary that returns
    true for any key.
    """

    def __getitem__(self, name):
        return name

    def has_key(self, name):
        """
        This is an infiniate dict. It has all keys.
        """
        return True
