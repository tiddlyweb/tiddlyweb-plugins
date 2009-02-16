"""
A very simple bookmarking application that uses
TiddlyWeb as its datastore. This version is built
to work under googleappengine, but that's not 
really a requirement.

To run this we must put user.html and bookmarklet.html
in the apps working dir and add 'twoter' to
config['system_plugins'] in tiddlywebconfig.py.

There's a version of this running at

   http://tiddlyweb.appspot.com/twoter
"""

import urllib
import logging
import cgi

import os
from jinja2 import Environment, FileSystemLoader

from tiddlyweb.model.policy import Policy, UserRequiredError
from tiddlyweb.web.http import HTTP302
from tiddlyweb.web.util import server_base_url, recipe_url

from tiddlyweb.store import NoRecipeError, NoBagError, NoTiddlerError
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler

from tiddlyweb import control

template_env = Environment(loader=FileSystemLoader('.'))

def base(environ, start_response):
    """
    Where a user comes to /twoter redirect to 
    their own location, or if they aren't logged
    in, have them log in.
    """
    user = environ['tiddlyweb.usersign']['name']
    if user == 'GUEST':
        raise UserRequiredError, 'real user required to twote'
    else:
        raise HTTP302, '%s/twoter/%s' % (server_base_url(environ), urllib.quote(user))

def user(environ, start_response):
    """
    Display an information page for the user. If they are not
    logged in, have them log in.
    """
    userpath = environ['wsgiorg.routing_args'][1]['username']
    user = environ['tiddlyweb.usersign']['name']
    if user == 'GUEST':
        raise UserRequiredError, 'real user required to twote'
    if user != userpath:
        raise HTTP302, '%s/twoter/%s' % (server_base_url(environ), urllib.quote(user))

    recent_recipe = _check_recipe('recent', environ, user)
    all_recipe = _check_recipe('all', environ, user)

    def recipe_href(recipe, extension):
        return '%s/tiddlers%s?filter=%s' % (
                recipe_url(environ, recipe), extension, urllib.quote('[sort[-modified]]')
                )

    template_values = {
            'user': user,
            'recent_url': recipe_href(recent_recipe, ''),
            'recent_feed': recipe_href(recent_recipe, '.atom'),
            'recent_wiki_d': recipe_href(recent_recipe, '.wiki') + '&amp;download=twoter-recent.html',
            'recent_wiki': recipe_href(recent_recipe, '.wiki'),
            'recent_json': recipe_href(recent_recipe, '.json'),
            'all_url': recipe_href(all_recipe, ''),
            'all_wiki_d': recipe_href(all_recipe, '.wiki') + '&amp;download=twoter-recent.html',
            'all_wiki': recipe_href(all_recipe, '.wiki'),
            'all_json': recipe_href(all_recipe, '.json'),
            'twoter_url': '%s/twoter/%s' % (server_base_url(environ), urllib.quote(user)),
            }

    environ['tiddlyweb.title'] = 'Twoter for %s' % user

    start_response('200 OK', [
        ('Content-Type', 'text/html')
        ])
    template = template_env.get_template('user.html')
    return template.generate(template_values)


def submit(environ, start_response):
    """
    Take POSTed input, put it in a Tiddler and save
    it into the store, and redirect back to the user
    page.
    """
    user = environ['tiddlyweb.usersign']['name']
    if user == 'GUEST':
        raise UserRequiredError, 'real user required to twote'

    recent_recipe = _check_recipe('recent', environ, user)
    all_recipe = _check_recipe('all', environ, user)

    tiddler = _make_tiddler(environ, user)

    bag = control.determine_bag_for_tiddler(all_recipe, tiddler)
    tiddler.bag = bag.name

    store = environ['tiddlyweb.store']

    original_title = tiddler.title
    tester_tiddler = Tiddler(original_title, bag=bag.name)
    addendum = 2
    while 1:
        try:
            tester_tiddler = store.get(tester_tiddler)
            new_title = '%s-%s' % (original_title, addendum)
            tiddler.title = new_title
            tester_tiddler.title = new_title
            addendum += 1
        except NoTiddlerError:
            store.put(tiddler)
            break

    raise HTTP302, '%s/twoter/%s' % (server_base_url(environ), urllib.quote(user))

def _make_tiddler(environ, user):
    """
    Slice and dice the input to make it into a tiddler.
    """
    posted_data = environ['tiddlyweb.query']
    charset = posted_data.get('charset', ['UTF-8'])[0]
    url = posted_data.get('url', [''])[0]
    title = posted_data.get('title', [''])[0]
    title = unicode(title, charset, 'replace')
    snip = posted_data.get('snip', [''])[0]
    snip = unicode(snip, charset, 'replace')
    tiddler_title = title.replace('.', '_')
    tiddler_text_title = title.replace('|', ' ')
    tiddler = Tiddler(tiddler_title)
    tiddler.tags = [u'twoted']
    tiddler.modifier = user
    tiddler.text = '[[%s|%s]]\n\n%s' % (tiddler_text_title, url, snip)
    return tiddler

def _check_recipe(name, environ, user):
    """
    Get the user's recipes, create them if required.
    """
    store = environ['tiddlyweb.store']

    recipe_name = '%s-%s' % (user, name)
    recipe_name = recipe_name.replace('.', '_')
    try:
        recipe = Recipe(recipe_name)
        recipe = store.get(recipe)
    except NoRecipeError:
        bag = _check_bag('all', environ, user)
        recipe.set_recipe([
            [u'TiddlyWeb', u''],
            [unicode(bag.name), unicode(_filter_string(name))],
            ])
        recipe.desc = '%s twotes for %s' % (name, user)
        store.put(recipe)
    return recipe

def _check_bag(name, environ, user):
    """
    Get the user's bag. Create if required.
    """
    store = environ['tiddlyweb.store']

    name = '%s-%s' % (user, name)
    name = name.replace('.', '_')
    try:
        bag = Bag(name)
        bag = store.get(bag)
    except NoBagError:
        uni_user = unicode(user)
        policy = Policy(owner=uni_user, manage=[uni_user],
                read=[uni_user], write=[uni_user],
                delete=[uni_user], create=[uni_user])
        bag.policy = policy
        bag.desc = 'Twotes for %s' % uni_user;
        store.put(bag)
    return bag

def _filter_string(name):
    if name == 'all':
        return '[sort[-modified]]'
    else:
        return '[sort[-modified]] [count[10]]'

def init(config):
    config['selector'].add('/twoter', GET=base)
    config['selector'].add('/twoter/{username:segment}', GET=user, POST=submit)
