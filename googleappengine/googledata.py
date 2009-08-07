"""
A StorageInterface that stores in Google Data.
"""

import logging

from base64 import b64encode, b64decode

from google.appengine.ext import db

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import Policy
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.serializer import Serializer
from tiddlyweb.store import NoBagError, NoRecipeError, NoTiddlerError
from tiddlyweb.stores import StorageInterface

class GDRecipe(db.Model):
    name = db.StringProperty(required=True)
    recipe = db.ListProperty(unicode)
    desc = db.StringProperty()
    owner = db.StringProperty()
    read = db.ListProperty(unicode)
    write = db.ListProperty(unicode)
    create = db.ListProperty(unicode)
    delete_ = db.ListProperty(unicode)
    manage = db.ListProperty(unicode)
    accept = db.ListProperty(unicode)

class GDBag(db.Model):
    name = db.StringProperty(required=True)
    desc = db.StringProperty()
    tiddlers = db.ListProperty(unicode)
    owner = db.StringProperty()
    read = db.ListProperty(unicode)
    write = db.ListProperty(unicode)
    create = db.ListProperty(unicode)
    delete_ = db.ListProperty(unicode)
    manage = db.ListProperty(unicode)
    accept = db.ListProperty(unicode)

class GDTiddler(db.Expando):
    title = db.StringProperty(required=True)
    modifier = db.StringProperty()
    modified = db.StringProperty()
    created = db.StringProperty()
    tags = db.ListProperty(unicode)
    text = db.TextProperty()
    bag = db.StringProperty()
    type = db.StringProperty()

class Store(StorageInterface):

    def _recipe_key(self, name):
        return 'key:recipe:%s' % name

    def _bag_key(self, name):
        return 'key:bag:%s' % name

    def _tiddler_key(self, tiddler):
        return 'key:tiddler:%s:%s' % (tiddler.bag, tiddler.title)

    def recipe_get(self, recipe):
        gdrecipe = GDRecipe.get_by_key_name(self._recipe_key(recipe.name))

        if not gdrecipe:
            raise NoRecipeError
        
        recipe_list = []
        for line in gdrecipe.recipe:
            bag, filter = line.split('?')
            recipe_list.append([bag, filter])

        recipe.set_recipe(recipe_list)
        recipe.desc = gdrecipe.desc
        policy = Policy(owner=gdrecipe.owner, read=gdrecipe.read, write=gdrecipe.write, create=gdrecipe.create, delete=gdrecipe.delete_, manage=gdrecipe.manage, accept=gdrecipe.accept)
        recipe.policy = policy
        return recipe

    def recipe_put(self, recipe):
        gdrecipe = GDRecipe(key_name=self._recipe_key(recipe.name), name=recipe.name)
        recipe_list = []
        for bag, filter in recipe.get_recipe():
            line = '%s?%s' % (bag, filter)
            recipe_list.append(line)
        gdrecipe.recipe = recipe_list
        gdrecipe.desc = recipe.desc
        gdrecipe.read = recipe.policy.read
        gdrecipe.write = recipe.policy.write
        gdrecipe.create = recipe.policy.create
        gdrecipe.delete_ = recipe.policy.delete
        gdrecipe.manage = recipe.policy.manage
        gdrecipe.accept = recipe.policy.accept
        gdrecipe.owner = recipe.policy.owner
        gdrecipe.put()

    def bag_get(self, bag):
        gdbag = GDBag.get_by_key_name(self._bag_key(bag.name))

        if not gdbag:
            raise NoBagError

        bag_tiddler_query = GDTiddler.gql('WHERE bag = :1')
        bag_tiddler_query.bind(bag.name)
        
        bag.desc = gdbag.desc
        policy = Policy(owner=gdbag.owner, read=gdbag.read,
                write=gdbag.write, create=gdbag.create, delete=gdbag.delete_,
                manage=gdbag.manage, accept=gdbag.accept)
        bag.policy = policy
        if not (hasattr(bag, 'skinny') and bag.skinny):
            for gdtiddler in bag_tiddler_query:
                tiddler = Tiddler(gdtiddler.title)
                bag.add_tiddler(tiddler)

        return bag

    def bag_put(self, bag):
        gdbag = GDBag(key_name=self._bag_key(bag.name), name=bag.name)
        gdbag.tiddlers = [tiddler.title for tiddler in bag.list_tiddlers()]
        gdbag.read = bag.policy.read
        gdbag.write = bag.policy.write
        gdbag.create = bag.policy.create
        gdbag.delete_ = bag.policy.delete
        gdbag.manage = bag.policy.manage
        gdbag.accept = bag.policy.accept
        gdbag.owner = bag.policy.owner
        gdbag.put()

    def tiddler_delete(self, tiddler):
        gdtiddler = GDTiddler.get_by_key_name(self._tiddler_key(tiddler))

        if not gdtiddler:
            raise NoTiddlerError, 'tiddler %s not found' % (tiddler.title)

        logging.info('deleting tiddler %s so trashing bag cache at %s' % (tiddler.title, tiddler.bag))
        gdtiddler.delete()

    def tiddler_get(self, tiddler):
        tiddler_properties = ['text', 'bag', 'modifier', 'modified', 'created', 'tags', 'type']
        gdtiddler = GDTiddler.get_by_key_name(self._tiddler_key(tiddler))

        if not gdtiddler:
            raise NoTiddlerError, 'tiddler %s not found' % (tiddler.title)

        # be explicit for now
        for item in tiddler_properties:
            tiddler.__setattr__(item, gdtiddler.__getattribute__(item))
        for item in gdtiddler.dynamic_properties():
            tiddler.fields[item] = gdtiddler.__getattr__(item)

        if tiddler.type and tiddler.type != 'None':
            tiddler.text = b64decode(tiddler.text.lstrip().rstrip())
        # explicitly set the tiddler revision to 1 since we don't support
        # revisions.
        tiddler.revision = 1
        return tiddler

    def tiddler_put(self, tiddler):
        if tiddler.type and tiddler.type != 'None':
            tiddler.text = b64encode(tiddler.text)
        gdtiddler = GDTiddler(key_name=self._tiddler_key(tiddler), title=tiddler.title, bag=tiddler.bag)
        gdtiddler.modifier = tiddler.modifier
        gdtiddler.modified = tiddler.modified
        gdtiddler.created = tiddler.created
        if not tiddler.text:
            tiddler.text = ''
        gdtiddler.text = tiddler.text
        gdtiddler.tags = tiddler.tags
        gdtiddler.type = tiddler.type
        for key in tiddler.fields:
            if not key.startswith('server.') and key != 'title':
                logging.warning('attempting to set key %s' % key)
                gdtiddler.__setattr__(key, db.Text(tiddler.fields[key]))
        gdtiddler.put()

    def user_get(self, user):
        pass

    def user_put(self, user):
        pass

    def list_recipes(self):
        q = GDRecipe.all()

        recipes = []
        try:
            for gdrecipe in q:
                recipe = Recipe(gdrecipe.name)
                recipe_list = []
                for line in gdrecipe.recipe:
                    bag, filter = line.split('?')
                    recipe_list.append([bag, filter])
                recipe.set_recipe(recipe_list)
                recipes.append(recipe)
        except TypeError:
            pass

        return recipes

    def list_bags(self):
        q = GDBag.all()

        try:
            return [Bag(bag.name) for bag in q]
        except TypeError:
            return []
