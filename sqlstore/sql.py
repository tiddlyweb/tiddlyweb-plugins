import logging

from tiddlyweb.stores import StorageInterface

from tiddlyweb.store import NoBagError, NoRecipeError, NoTiddlerError, NoUserError

from sqlalchemy import ForeignKey, Column, String, Integer, create_engine
from sqlalchemy.sql import and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, backref

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from tiddlyweb.model.tiddler import string_to_tags_list, Tiddler
from tiddlyweb.model.policy import Policy
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.serializer import Serializer

from uuid import uuid4 as uuid

Base = declarative_base()

class sRevision(Base):
    __tablename__ = 'revisions'

    id = Column(String, primary_key=True)
    tiddler_id = Column(String, ForeignKey('tiddlers.id'))
    modifier = Column(String)
    modified = Column(String)
    tags = Column(String)
    text = Column(String)
    revision_id = Column(Integer, nullable=False)

    def __init__(self):
        self.id = str(uuid())

    def __repr__(self):
        return "<sRevision('%s:%s:%s')>" % (self.id, self.revision_id, self.tiddler.title)


class sTiddler(Base):
    __tablename__ = 'tiddlers'

    id = Column(String)
    title = Column(String, primary_key=True)
    bag_name = Column(String, ForeignKey('bags.name'), primary_key=True)

    revisions = relation(sRevision, primaryjoin=sRevision.tiddler_id==id, 
            order_by=sRevision.revision_id, cascade='delete')

    def revision(self):
        if self.rev:
            return self.revisions[self.rev - 1]
        return self.revisions[-1]

    def created(self):
        return self.revisions[0].modified

    def __init__(self, title, bag_name, rev=None):
        self.id = str(uuid())
        self.title = title
        self.bag_name = bag_name
        self.rev = rev

    def __repr__(self):
        return "<sTiddler('%s:%s:%s')>" % (self.bag_name, self.title, self.id)


sRevision.tiddler = relation(sTiddler, primaryjoin=sTiddler.id==sRevision.tiddler_id)


class sPolicy(Base):
    __tablename__ = 'policies'

    id = Column(Integer, primary_key=True)
    read = Column(String)
    write = Column(String)
    delete = Column(String)
    create = Column(String)
    manage = Column(String)
    owner = Column(String)


class sBag(Base):
    __tablename__ = 'bags'

    name = Column(String, primary_key=True)
    desc = Column(String)
    policy_id = Column(Integer, ForeignKey('policies.id'))

    tiddlers = relation(sTiddler, backref='bag', primaryjoin=sTiddler.bag_name==name, cascade='delete')
    policy = relation(sPolicy, uselist=False)

    # setting policy to a string for now
    def __init__(self, name, desc=''):
        self.name = name
        self.desc = desc

    def __repr__(self):
        return "<sBag('%s')>" % (self.name)

class sRecipe(Base):
    __tablename__ = 'recipes'

    name = Column(String, primary_key=True)
    desc = Column(String)
    recipe_string = Column(String, default='')
    policy_id = Column(Integer, ForeignKey('policies.id'))

    policy = relation(sPolicy, uselist=False)

    def __init__(self, name, desc=''):
        self.name = name
        self.desc = desc

    def __repr__(self):
        return "<sRecipe('%s')>" % (self.name)

class sRole(Base):
    __tablename__ = 'roles'

    usersign = Column(String, ForeignKey('users.usersign'), primary_key=True)
    role_name = Column(String, primary_key=True)
    
class sUser(Base):
    __tablename__ = 'users'

    usersign = Column(String, primary_key=True)
    note = Column(String)
    password = Column(String)
    
    roles = relation(sRole, primaryjoin=sRole.usersign==usersign)

    def __repr__(self):
        return "<sUser('%s:%s')>" % (self.name, self.roles)


#Base.metadata.drop_all(engine)
#Base.metadata.create_all(engine)

class Store(StorageInterface):

    def __init__(self, environ=None):
        super(Store, self).__init__(environ)
        self._init_store()

    def _init_store(self):
        self.engine = create_engine('sqlite:///test.db')
        self.serializer = Serializer('text')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def recipe_delete(self, recipe):
        try:
            srecipe = self.session.query(sRecipe).filter(sRecipe.name==recipe.name).one()
            self.session.delete(srecipe)
            self.session.commit()
        except NoResultFound, exc:
            raise NoRecipeError('no results for recipe %s, %s' % (recipe.name, exc))

    def recipe_get(self, recipe):
        try:
            srecipe = self.session.query(sRecipe).filter(sRecipe.name==recipe.name).one()
            recipe = self._map_recipe(recipe, srecipe)
            return recipe
        except NoResultFound, exc:
            raise NoRecipeError('no results for recipe %s, %s' % (recipe.name, exc))

    def _map_recipe(self, recipe, srecipe):
        recipe.desc = srecipe.desc
        recipe.policy = self._map_policy(srecipe.policy)
        recipe.set_recipe(self._map_recipe_string(srecipe.recipe_string))
        return recipe

    def _map_recipe_string(self, recipe_string):
        recipe = []
        if recipe_string:
            for line in recipe_string.split('\n'):
                bag, filter = line.split('?', 1)
                recipe.append([bag, filter])
        return recipe

    def recipe_put(self, recipe):
        srecipe = self._map_srecipe(recipe)
        self.session.merge(srecipe)
        self.session.commit()

    def _map_srecipe(self, recipe):
        srecipe = sRecipe(recipe.name, recipe.desc)
        srecipe.policy = self._map_spolicy(recipe.policy)
        srecipe.recipe_string = self._map_srecipe_string(recipe)
        return srecipe

    def _map_srecipe_string(self, recipe_list):
        string = ''
        string += '\n'.join(['%s?%s' % (bag, filter_string) for bag, filter_string in recipe_list])
        return string

    def bag_delete(self, bag):
        try:
            sbag = self.session.query(sBag).filter(sBag.name==bag.name).one()
            self.session.delete(sbag)
            self.session.commit()
        except NoResultFound, exc:
            raise NoBagError('Bag %s not found: %s' % (bag.name, exc))

    def bag_get(self, bag):
        logging.debug('attempting to get bag: %s' % bag.name)
        try:
            sbag = self.session.query(sBag).filter(sBag.name == bag.name).one()
            bag = self._map_bag(bag, sbag)

            if not (hasattr(bag, 'skinny') and bag.skinny):
                tiddlers = sbag.tiddlers
                for tiddler in tiddlers:
                    bag.add_tiddler(Tiddler(tiddler.title))
            return bag
        except NoResultFound, exc:
            raise NoBagError('Bag %s not found: %s' % (bag.name, exc))

    def _map_bag(self, bag, sbag):
        bag.desc = sbag.desc
        bag.policy = self._map_policy(sbag.policy)
        return bag

    def bag_put(self, bag):
        sbag = self._map_sbag(bag)
        self.session.merge(sbag)
        self.session.commit()

    def _map_sbag(self, bag):
        sbag = sBag(bag.name, bag.desc)
        sbag.policy = self._map_spolicy(bag.policy)
        return sbag

    def _map_spolicy(self, policy):
        spolicy = sPolicy()
        spolicy.owner = policy.owner
        for field in ['read', 'write', 'delete', 'create', 'manage']:
            setattr(spolicy, field, self._map_spolicy_rule(getattr(policy, field)))
        return spolicy

    def _map_policy(self, spolicy):
        policy = Policy()
        policy.owner = spolicy.owner
        for field in ['read', 'write', 'delete', 'create', 'manage']:
            setattr(policy, field, self._map_policy_rule(getattr(spolicy, field)))
        return policy

    def _map_spolicy_rule(self, field_list):
        if field_list:
            field_value = ','.join(['"%s"' % name for name in field_list])
            if field_value:
                field_value = '[' + field_value + ']'
            else:
                field_value = None
        else:
            field_value = None
        return field_value

    def _map_policy_rule(self, field_string):
        if field_string:
            field_string = field_string.strip('["').rstrip('"]')
            return field_string.split('","')
        return []

    def tiddler_delete(self, tiddler):
        try:
            stiddler = (self.session.query(sTiddler).
                    filter(sTiddler.title==tiddler.title).
                    filter(sTiddler.bag_name==tiddler.bag).one())
            self.session.delete(stiddler)
            self.session.commit()
        except NoResultFound, exc:
            raise NoTiddlerError('no tiddler %s to delete, %s' % (tiddler.title, exc))

    def tiddler_get(self, tiddler):
        try:
            stiddler = (self.session.query(sTiddler).
                    filter(sTiddler.title==tiddler.title).
                    filter(sTiddler.bag_name==tiddler.bag).one())
            if tiddler.revision:
                stiddler.rev = tiddler.revision
            else:
                stiddler.rev = None
            tiddler = self._map_tiddler(tiddler, stiddler)
            return tiddler
        except NoResultFound, exc:
            raise NoTiddlerError('Tiddler %s not found: %s' % (tiddler.title, exc))


    def _map_tiddler(self, tiddler, stiddler):
        try:
            tiddler.modifier = stiddler.revision().modifier
            tiddler.modified = stiddler.revision().modified
            tiddler.revision = stiddler.revision().revision_id
            tiddler.text = stiddler.revision().text
            tiddler.tags = self._map_tags(stiddler.revision().tags)
            return tiddler
        except IndexError, exc:
            raise NoTiddlerError('No revision %s for tiddler %s, %s' % (stiddler.rev, stiddler.title, exc))

    def _map_tags(self, tags_string):
        return string_to_tags_list(tags_string)

    def tiddler_put(self, tiddler):
        stiddler = self._map_stiddler(tiddler)
        self.session.merge(stiddler)
        self.session.commit()

    def _map_stiddler(self, tiddler):
        try:
            stiddler = (self.session.query(sTiddler).
                    filter(sTiddler.title == tiddler.title).
                    filter(sTiddler.bag_name == tiddler.bag).one())
        except NoResultFound:
            stiddler = sTiddler(tiddler.title, tiddler.bag)
        srevision = sRevision()
        srevision.tiddler_id = stiddler.id
        srevision.modified = tiddler.modified
        srevision.modifier = tiddler.modifier
        srevision.text = tiddler.text
        srevision.tags = self._map_stags(tiddler.tags)
        try:
            srevision.revision_id = stiddler.revisions[-1].revision_id + 1
        except IndexError:
            srevision.revision_id = 1
        self.session.add(srevision)
        return stiddler

    def _map_stags(self, tags):
        return self.serializer.serialization.tags_as(tags)

    def user_delete(self, user):
        try:
            suser = self.session.query(sUser).filter(sUser.usersign==user.usersign).one()
            self.session.delete(suser)
            self.session.commit()
        except NoResultFound, exc:
            raise NoUserError('user %s not found, %s' % (user.name, exc))

    def user_get(self, user):
        try:
            suser = self.session.query(sUser).filter(sUser.usersign==user.usersign).one()
            user = self._map_user(user, suser)
            return user
        except NoResultFound, exc:
            raise NoUserError('user %s not found, %s' % (user.name, exc))

    def _map_user(self, user, suser):
        user.usersign = suser.usersign
        user._password = suser.password
        user.note = suser.note
        user.roles = suser.roles
        return user

    def user_put(self, user):
        suser = self._map_suser(user)
        self.session.merge(suser)
        self.session.commit()

    def _map_suser(self, user):
        suser = sUser()
        suser.usersign = user.usersign
        suser.password = user._password
        suser.note = user.note
        suser.roles = list(user.roles)
        return suser

    def list_recipes(self):
        return [self._map_recipe(Recipe(srecipe.name), srecipe) for srecipe in self.session.query(sRecipe).all()]

    def list_bags(self):
        return [self._map_bag(Bag(sbag.name), sbag) for sbag in self.session.query(sBag).all()]

    def list_users(self):
        return [self._map_user(suser) for suser in self.session.query(sUser).all()]

    def list_tiddler_revisions(self, tiddler):
        try:
            stiddler = (self.session.query(sTiddler).
                    filter(sTiddler.title==tiddler.title).
                    filter(sTiddler.bag_name==tiddler.bag).one())
        except NoResultFound, exc:
            raise NoTiddlerError('tiddler %s not found, %s' % (tiddler.title, exc))
        return [revision.revision_id for revision in reversed(stiddler.revisions)]
