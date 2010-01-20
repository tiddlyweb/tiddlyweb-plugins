"""
A tool for importing a TiddlyWiki into a TiddlyWeb,
via the web, either by uploading a file or providing
a URL. This differs from other tools in that it provides
a selection system.

This is intentionally a UI driven thing, rather than API
driven.

Two templates are used 'chooser.html' and 'wimport.html'.
These may be overridden locally. See tiddlywebplugins.templates.
"""

import cgi
import operator
import urllib2

from uuid import uuid4 as uuid

from tiddlywebplugins.utils import entitle, do_html
from tiddlywebplugins.templates import get_template
from tiddlywebplugins.twimport import import_one, wiki_string_to_tiddlers

from tiddlyweb.control import filter_tiddlers_from_bag
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import ForbiddenError, UserRequiredError
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import NoBagError
from tiddlyweb.web.util import bag_url
from tiddlyweb.web.http import HTTP302

def init(config):
    config['selector'].add('/import', GET=interface, POST=wimport)


@entitle('Import Tiddlers')
@do_html()
def interface(environ, start_response):
    return _send_wimport(environ, start_response)


@entitle('Import Tiddlers')
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
        return _process_choices(environ, start_response, form)
    else:
        return _send_wimport(environ, start_response, 'missing field info')

def _process_choices(environ, start_response, form):
    store = environ['tiddlyweb.store']
    user = environ['tiddlyweb.usersign']

    tmp_bag = form['tmpbag'].value
    bag = form['bag'].value

    bag = Bag(bag)
    try:
        bag.skinny = True
        bag = store.get(bag)
        bag.policy.allows(user, 'write')
    except NoBagError:
        return _send_wimport(environ, start_response, 'chosen bag does not exist')
    except (ForbiddenError, UserRequiredError):
        return _send_wimport(environ, start_response, 'you may not write to that bag')

    tiddler_titles = form.getlist('tiddler')
    for title in tiddler_titles:
        tiddler = Tiddler(title, tmp_bag)
        tiddler = store.get(tiddler)
        tiddler.bag = bag.name
        store.put(tiddler)
    tmp_bag = Bag(tmp_bag)
    store.delete(tmp_bag)
    bagurl = bag_url(environ, bag) + '/tiddlers'
    raise HTTP302(bagurl)


def _show_chooser(environ, bag):
    # refresh the bag object
    store = environ['tiddlyweb.store']
    bag.skinny = True
    bag = store.get(bag)
    tiddlers = filter_tiddlers_from_bag(bag, 'sort=title')
    template = get_template(environ, 'chooser.html')
    return template.generate(tiddlers=tiddlers,
            tmpbag=bag.name,
            bags=_get_bags(environ))


def _process_url(environ, url):
    tmp_bag = _make_bag(environ)
    import_one(tmp_bag.name, url, environ['tiddlyweb.store'])
    return tmp_bag

def _process_file(environ, filehandle):
    tmp_bag = _make_bag(environ)
    wikitext = filehandle.read().decode('utf-8')
    filehandle.close()
    tiddlers = wiki_string_to_tiddlers(wikitext)
    store = environ['tiddlyweb.store']
    for tiddler in tiddlers:
        tiddler.bag = tmp_bag.name
        store.put(tiddler)
    return tmp_bag


def _make_bag(environ):
    store = environ['tiddlyweb.store']
    bag_name = str(uuid())
    bag = Bag(bag_name)
    _set_restricted_policy(environ, bag)
    store.put(bag)
    return bag

def _set_restricted_policy(environ, bag):
    """
    Set this bag to only be visible and usable by
    the current user, if the current user is not
    guest.
    """
    username = environ['tiddlyweb.usersign']['name']
    if username == 'GUEST':
        return
    bag.policy.owner = username
    # accept does not matter here
    for constraint in ['read', 'write', 'create', 'delete', 'manage']:
        setattr(bag.policy, constraint, [username])
    return


def _send_wimport(environ, start_response, message=''):
    template = get_template(environ, 'wimport.html')
    return template.generate(message=message)


def _get_bags(environ):
# XXX we need permissions handling here
    store = environ['tiddlyweb.store']
    user = environ['tiddlyweb.usersign']
    bags = store.list_bags()
    kept_bags = []
    for bag in bags:
        bag = store.get(bag)
        try:
            bag.policy.allows(user, 'write')
            kept_bags.append(bag)
            continue
        except (ForbiddenError, UserRequiredError):
            pass

    return sorted(kept_bags, key=operator.attrgetter('name'))
