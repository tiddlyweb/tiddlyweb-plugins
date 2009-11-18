"""
A tool for importing a TiddlyWiki into a TiddlyWeb,
via the web, either by uploading a file or providing
a URL. This differs from other tools in that it provides
a selection system.

This is intentionally a UI driven thing, rather than API
driven.
"""

import cgi
import urllib2

from uuid import uuid4 as uuid

from jinja2 import Environment, FileSystemLoader
template_env = Environment(loader=FileSystemLoader('templates'))

from tiddlywebplugins.utils import entitle, do_html
from tiddlywebwiki.tiddlywiki import import_wiki, import_wiki_file

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.web.util import bag_url
from tiddlyweb.web.http import HTTP302

def init(config):
    config['selector'].add('/import', GET=interface, POST=wimport)


@entitle('Import a Wiki')
@do_html()
def interface(environ, start_response):
    return _send_wimport(environ, start_response)


@entitle('Import a Wiki')
@do_html()
def wimport(environ, start_response):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
    if 'url' in form or 'file' in form:
        try:
            if form['url'].value:
                tmp_bag = _process_url(environ, form['url'].value)
            if form['file'].filename:
                tmp_bag = _process_file(environ, form['file'].file)
            return _show_chooser(environ, tmp_bag)
        except AttributeError: # content was not right
            return _send_wimport(environ, start_response, 'that was not a wiki')
        except ValueError: # file or url was not right
            return _send_wimport(environ, start_response, 'could not read that')
    elif 'bag' in form:
        return _process_choices(environ, form)
    else:
        return _send_wimport(environ, start_response, 'missing field info')

def _process_choices(environ, form):
    store = environ['tiddlyweb.store']
    bag = form['bag'].value
    tmp_bag = form['tmpbag'].value
    tiddler_titles = form.getlist('tiddler')
    for title in tiddler_titles:
        tiddler = Tiddler(title, tmp_bag)
        tiddler = store.get(tiddler)
        tiddler.bag = bag
        store.put(tiddler)
    tmp_bag = Bag(tmp_bag)
    store.delete(tmp_bag)
    bag = Bag(bag)
    bagurl = bag_url(environ, bag) + '/tiddlers'
    raise HTTP302(bagurl)


def _show_chooser(environ, bag):
    # refresh the bag object
    store = environ['tiddlyweb.store']
    bag = store.get(bag)
    template = template_env.get_template('chooser.html')
    return template.generate(tiddlers=bag.gen_tiddlers(),
            tmpbag=bag.name,
            bags=_get_bags(environ))


def _process_url(environ, url):
    file = urllib2.urlopen(url)
    return _process_file(environ, file)

def _process_file(environ, file):
    tmp_bag = _make_bag(environ)
    wikitext = ''
    while 1:
        line = file.readline()
        if not line:
            break
        wikitext += unicode(line, 'utf-8')
    import_wiki(environ['tiddlyweb.store'], wikitext, tmp_bag.name)
    file.close()
    return tmp_bag


def _make_bag(environ):
    store = environ['tiddlyweb.store']
    bag_name = str(uuid())
    bag = Bag(bag_name)
    store.put(bag)
    return bag


def _send_wimport(environ, start_response, message=''):
    template = template_env.get_template('wimport.html')
    return template.generate(message=message)


def _get_bags(environ):
# XXX we need permissions handling here
    store = environ['tiddlyweb.store']
    bags = store.list_bags()
    return bags
