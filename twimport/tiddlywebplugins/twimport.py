"""
Import tiddlers, Cook recipes, TiddlyWikis into TiddlyWeb.
"""

import os
import urllib2
import urlparse

from html5lib import HTMLParser, treebuilders

from tiddlyweb.model.tiddler import Tiddler, string_to_tags_list
from tiddlyweb.serializer import Serializer
from tiddlyweb.manage import make_command

from tiddlywebplugins.utils import get_store

ACCEPTED_RECIPE_TYPES = ['tiddler', 'plugin', 'recipe']
ACCEPTED_TIDDLER_TYPES = ['js', 'tid', 'tiddler']


def init(config):
    """
    Initialize the plugin, establishing twanager commands.
    """

    @make_command()
    def twimport(args):
        """Import tiddlers, recipes, wikis, binary content: <bag> <URI>"""
        bag = args[0]
        urls = args[1:]
        if not bag or not urls:
            raise IndexError('missing args')
        import_list(bag, urls, get_store(config))


def import_list(bag_name, urls, store):
    """Import a list of URIs into bag."""
    for url in urls:
        import_one(bag_name, url, store)


def import_one(bag_name, url, store):
    """Import one URI into bag."""
    if url.endswith('.recipe'):
        tiddlers = [url_to_tiddler(tiddler_url) for
                tiddler_url in recipe_to_urls(url)]
    elif url.endswith('.wiki') or url.endswith('.html'):
        tiddlers = wiki_to_tiddlers(url)
    else: # we have a tiddler of some form
        tiddlers = [url_to_tiddler(url)]

    for tiddler in tiddlers:
        tiddler.bag = bag_name
        store.put(tiddler)


def recipe_to_urls(url):
    """
    Provided a url or path to a recipe, explode the recipe to
    a list of URLs of tiddlers (of various types).
    """
    url, handle = _get_url_handle(url)
    return _expand_recipe(handle.read().decode('utf-8', 'replace'), url)


def url_to_tiddler(url):
    """
    Given a url to a tiddlers of some form,
    return a Tiddler object.
    """
    url, handle = _get_url_handle(url)

    if url.endswith('.js'):
        tiddler = from_plugin(url, handle)
    elif url.endswith('.tid'):
        tiddler = from_tid(url, handle)
    elif url.endswith('.tiddler'):
        tiddler = from_tiddler(url, handle)
    else:
        # binary tiddler
        tiddler = from_special(url, handle)
    return tiddler


def wiki_to_tiddlers(url):
    """
    Retrieve a .wiki or .html and extract the contained tiddlers.
    """
    url, handle = _get_url_handle(url)
    return wiki_string_to_tiddlers(handle.read().decode('utf-8', 'replace'))


def wiki_string_to_tiddlers(content):
    """
    Turn a string that is a wiki into tiddler.
    """
    parser = HTMLParser(tree=treebuilders.getTreeBuilder('dom'))
    doc = parser.parse(content)
    # minidom will not provide working getElementById without
    # first having a valid document, which means some very specific
    # doctype hooey. So we traverse 
    body = doc.getElementsByTagName('body')[0]
    body_divs = body.getElementsByTagName('div')
    for div in body_divs:
        if div.hasAttribute('id') and div.getAttribute('id') == 'storeArea':
            divs = div.getElementsByTagName('div')
            break

    tiddlers = []
    for tiddler_div in divs:
        tiddlers.append(_get_tiddler_from_div(tiddler_div))
    return tiddlers


def from_plugin(uri, handle):
    """
    generates Tiddler from a JavaScript (and accompanying meta) file
    If there is no .meta file, title and tags assume default values.
    """
    default_title = _get_title_from_uri(uri)
    default_tags = "systemConfig"

    meta_uri = "%s.meta" % uri
    try:
        meta_content = _get_url(meta_uri)
    except (urllib2.HTTPError, urllib2.URLError, IOError, OSError):
        meta_content = "title: %s\ntags: %s\n" % (default_title, default_tags)
    try:
        title = [line for line in meta_content.split("\n")
                if line.startswith("title:")][0]
        title = title.split(":", 1)[1].strip()
    except IndexError:
        title = default_title
    tiddler_meta = "\n".join(line for line in meta_content.split("\n")
            if not line.startswith("title:")).rstrip()

    plugin_content = handle.read().decode('utf-8', 'replace')
    tiddler_text = "%s\n\n%s" % (tiddler_meta, plugin_content)

    return _from_text(title, tiddler_text)


def from_special(uri, handle):
    """
    This is borrowed from ben G's bimport.
    """
    title = _get_title_from_uri(uri)
    # XXX: will mime type guessing always work?
    content_type = handle.headers.type
    data = handle.read()

    tiddler = Tiddler(title)
    tiddler.type = content_type
    tiddler.text = data

    return tiddler


def from_tid(uri, handle):
    """
    generates Tiddler from a TiddlyWeb-style .tid file
    """
    title = _get_title_from_uri(uri)
    return _from_text(title, handle.read().decode('utf-8', 'replace'))


def from_tiddler(uri, handle):
    """
    generates Tiddler from a Cook-style .tiddler file
    """
    content = handle.read().decode('utf-8', 'replace')
    content = _escape_brackets(content)

    parser = HTMLParser(tree=treebuilders.getTreeBuilder('dom'))
    dom = parser.parse(content)
    node = dom.getElementsByTagName('div')[0]

    return _get_tiddler_from_div(node)


def _escape_brackets(content):
    """
    escapes angle brackets in tiddler's HTML representation
    """
    open_pre = content.index('<pre>')
    close_pre = content.rindex('</pre>')
    start = content[0:open_pre + 5]
    middle = content[open_pre + 5:close_pre]
    end = content[close_pre:]
    middle = middle.replace('>', '&gt;').replace('<', '&lt;')
    return start + middle + end


def _get_title_from_uri(uri):
    """
    Turn a uri of tiddler into the title of a tiddler,
    by looking at the final segment of the path.
    """
    title = uri.split("/")[-1]
    title = _strip_extension(title)
    title = urllib2.unquote(title)
    if not type(title) == unicode:
        title = unicode(title, "utf-8")
    return title


def _strip_extension(title):
    """
    If the title ends with a tiddler extension, then strip
    it off. Otherwise, leave it.
    """
    name, extension = title.rsplit('.', 1)
    if extension in ACCEPTED_TIDDLER_TYPES:
        return name
    else:
        return title


def _expand_recipe(content, url=''):
    urls = []
    for line in content.splitlines():
        line = line.lstrip().rstrip()
        try:
            target_type, target = line.split(':', 1)
        except ValueError:
            continue # blank line in recipe
        if target_type in ACCEPTED_RECIPE_TYPES:
            if isinstance(target, unicode):
                target = target.encode('utf-8')
            target = target.lstrip().rstrip()
            # Check to see if the target is a URL (has a scheme)
            # if not we want to join it to the current url before
            # carrying on.
            scheme, _ = urllib2.splittype(target)
            if not scheme:
                if not '%' in target:
                    target = urllib2.quote(target)
                target = urlparse.urljoin(url, target)
            if target_type == 'recipe':
                urls.extend(recipe_to_urls(target))
            else:
                urls.append(target)
    return urls



def _get_url(url):
    """
    Load a URL and decode it to unicode.
    """
    content = urllib2.urlopen(url).read().decode('utf-8', 'replace')
    return content.replace("\r", "")


def _from_text(title, content):
    """
    generates Tiddler from an RFC822-style string

    This corresponds to TiddlyWeb's text serialization of TiddlerS.
    """
    tiddler = Tiddler(title)
    serializer = Serializer("text")
    serializer.object = tiddler
    serializer.from_string(content)
    return tiddler


def _get_text(nodelist):
    """
    Traverse a list of dom nodes extracting contained text.
    """
    text = ''
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            text = text + node.data
        if node.childNodes:
            text = text + _get_text(node.childNodes)
    return text


def _get_tiddler_from_div(node):
    """
    Create a Tiddler from an HTML div element.
    """
    tiddler = Tiddler(node.getAttribute('title'))
    try:
        tiddler.text = _html_decode(_get_text(node.getElementsByTagName('pre')))
    except IndexError:
        # there are no contents in the tiddler
        tiddler.text = ''

    for attr, value in node.attributes.items():
        data = value
        if data and attr != 'tags':
            if attr in (['modifier', 'created', 'modified']):
                tiddler.__setattr__(attr, data)
            elif (attr not in ['title', 'changecount'] and
                    not attr.startswith('server.')):
                tiddler.fields[attr] = data
    if not node.attributes.get('modified', None) and tiddler.created:
        tiddler.modified = tiddler.created
    tiddler.tags = string_to_tags_list(str(node.getAttribute('tags')))

    return tiddler


def _get_url_handle(url):
    """
    Open the url using urllib2.urlopen. If the url is a filepath
    transform it into a file url.
    """
    try:
        try:
            handle = urllib2.urlopen(url)
        except urllib2.URLError:
            scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
            path = urllib2.quote(path)
            newurl = urlparse.urlunparse((scheme, netloc, path, params, query, fragment))
            handle = urllib2.urlopen(newurl)
    except ValueError:
        # If ValueError happens again we want it to raise
        url = 'file:' + os.path.abspath(url)
        handle = urllib2.urlopen(url)
    return url, handle


def _html_decode(text):
    """
    Decode HTML entities used in TiddlyWiki content into the 'real' things.
    """
    return text.replace('&gt;', '>').replace('&lt;', '<').replace(
            '&amp;', '&').replace('&quot;', '"')
