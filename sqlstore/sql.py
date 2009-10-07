"""
This is an implementation of the TiddlyWeb StorageInterface,
as defined in tiddlyweb.stores. It provides storage for
Tiddler, Bag, Recipe and User entities in an RDBMS via the
Python SQLAlchemy library.

The entities created are:

    fields:    The fields of a Tiddler revision.
    revisions: A specific revision of a Tiddler.
    tiddlers:  The name and bag of a Tiddler.
    policies:  A Policy, associated with a bag or recipe.
    bags:      A Bag.
    recipes:   A recipe.
    roles:     The roles associated with a User.
    users:     A User.
"""
import logging

from uuid import uuid4 as uuid
from base64 import b64encode, b64decode

from sqlalchemy import Table, ForeignKey, Column, String, Unicode, Integer, UnicodeText, create_engine
from sqlalchemy.sql import and_, or_, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, backref, mapper, sessionmaker, aliased
from sqlalchemy.orm.exc import NoResultFound

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import Policy
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler, string_to_tags_list
from tiddlyweb.model.user import User
from tiddlyweb.serializer import Serializer
from tiddlyweb.store import NoBagError, NoRecipeError, NoTiddlerError, \
        NoUserError
from tiddlyweb.stores import StorageInterface

EMPTY_TIDDLER = Tiddler('empty')

# Base class for declarative mapper classes.
Base = declarative_base()
Session = sessionmaker()

class sFieldName(Base):
    __tablename__ = 'field_names'
    id = Column('id', Integer, primary_key=True)
    name = Column('name', Unicode(256), index=True)


class sField(Base):
    """
    Mapper class for a single tiddler extended field.
    """
    __tablename__ = 'field_values'
    field_name_id = Column(Integer, ForeignKey('field_names.id'),
            primary_key=True, index=True)
    revision_id = Column(String(50), ForeignKey('revisions.id'),
            primary_key=True, index=True)
    value = Column(Unicode(1024), index=True)

    name = relation(sFieldName)


class sRevision(Base):
    """
    Mapper class for a single tiddler revision.

    These are the parts of a tiddler that may change
    between revisions.
    """
    __tablename__ = 'revisions'

    id = Column(String(50), primary_key=True, index=True)
    tiddler_id = Column(String(50), ForeignKey('tiddlers.id'), index=True)
    modifier = Column(Unicode(256))
    modified = Column(String(14))
    type = Column(String(128))
    tags = Column(Unicode(1024))
    text = Column(UnicodeText, default='')
    revision_id = Column(Integer, nullable=False, index=True)

    fields = relation(sField, backref='revision', cascade='delete', lazy=False)

    def __init__(self):
        self.id = str(uuid())

    def __repr__(self):
        return "<sRevision('%s:%s:%s')>" % (self.id, self.revision_id, self.tiddler.title)


class sTiddler(Base):
    """
    Mapper class for a single tiddler in a bag.
    Has a relation to all its revisions.
    """
    __tablename__ = 'tiddlers'

    id = Column(String(50), unique=True, index=True)
    title = Column(Unicode(128), primary_key=True, index=True)
    bag_name = Column(Unicode(128), ForeignKey('bags.name'), primary_key=True, index=True)

    revisions = relation(sRevision, primaryjoin=sRevision.tiddler_id==id, 
            order_by=sRevision.revision_id, cascade='delete')

    current_revision = relation(sRevision, primaryjoin=sRevision.tiddler_id==id, 
            order_by=sRevision.revision_id.desc(), cascade='delete', uselist=False,
            lazy=False)

    def revision(self):
        """
        Calculate the current revision of this tiddler.
        """
        if self.rev:
            return self.revisions[self.rev - 1]
        return self.revisions[-1]

    def created(self):
        """
        Calculate the created field for this tiddler from
        the first revision.
        """
        return self.revisions[0].modified

    def __init__(self, title, bag_name, rev=None):
        self.id = str(uuid())
        self.title = title
        self.bag_name = bag_name
        self.rev = rev

    def __repr__(self):
        return "<sTiddler('%s:%s:%s')>" % (self.bag_name, self.title, self.id)


# Establish the relation between a revision and its Tiddler
sRevision.tiddler = relation(sTiddler, primaryjoin=sTiddler.id==sRevision.tiddler_id)


class sPolicy(object):
    """
    Empty mapper class for a policy.
    """
    pass
# The policies table. Each constraint's value is a 
# string that looks a bit like a list.
policies = Table('policies', Base.metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('read', Unicode(2048)),
        Column('write', Unicode(2048)),
        Column('delete', Unicode(2048)),
        Column('create', Unicode(2048)),
        Column('manage', Unicode(2048)),
        Column('accept', Unicode(2048)),
        Column('owner', Unicode(2048))
    )
# map the sPolicy class to the policies table
mapper(sPolicy, policies)

class sBag(Base):
    """
    Mapper class representing a Bag.
    Has relations to its policy and the tiddlers it contains.
    """
    __tablename__ = 'bags'

    name = Column(Unicode(256), primary_key=True, index=True)
    desc = Column(Unicode(1024))
    policy_id = Column(Integer, ForeignKey('policies.id'), index=True)

    tiddlers = relation(sTiddler, backref='bag', primaryjoin=sTiddler.bag_name==name, cascade='delete')
    policy = relation(sPolicy, uselist=False, lazy=False)

    # setting policy to a string for now
    def __init__(self, name, desc=''):
        self.name = name
        self.desc = desc

    def __repr__(self):
        return "<sBag('%s')>" % (self.name)


class sRecipe(Base):
    """
    Mapper class for a recipe.
    Has a relation to its policy.
    """
    __tablename__ = 'recipes'

    name = Column(Unicode(256), primary_key=True, index=True)
    desc = Column(Unicode(1024))
    recipe_string = Column(UnicodeText, default=u'')
    policy_id = Column(Integer, ForeignKey('policies.id'), index=True)

    policy = relation(sPolicy, uselist=False, lazy=False)

    def __init__(self, name, desc=''):
        self.name = name
        self.desc = desc

    def __repr__(self):
        return "<sRecipe('%s')>" % (self.name)


class sRole(Base):
    __tablename__ = 'roles'

    usersign = Column(Unicode(256), ForeignKey('users.usersign'), primary_key=True, index=True)
    role_name = Column(Unicode(50), primary_key=True)

    def __repr__(self):
        return "<sRole('%s:%s')>" % (self.usersign, self.role_name)
    

class sUser(Base):
    __tablename__ = 'users'

    usersign = Column(Unicode(256), primary_key=True, index=True)
    note = Column(Unicode(1024))
    password = Column(String(128))
    
    roles = relation(sRole, primaryjoin=sRole.usersign==usersign, cascade='delete',
            lazy=False)

    def __repr__(self):
        return "<sUser('%s:%s')>" % (self.usersign, self.roles)


class Store(StorageInterface):
    """
    A SqlAlchemy based storage interface for TiddlyWeb.
    """

    session = None

    def __init__(self, environ=None):
        super(Store, self).__init__(environ)
        self._init_store()

    def _init_store(self):
        """
        Establish the database engine and session,
        creating tables if needed.
        """
        store_type = self._db_config().split(':', 1)[0]
        if store_type == 'sqlite' or not Store.session:
            engine = create_engine(self._db_config(), pool_recycle=3600)
            Base.metadata.create_all(engine)
            Session.configure(bind=engine)
            Store.session = Session()
        self.session = Store.session
        self.serializer = Serializer('text')

    def _db_config(self):
        store_config = self.environ['tiddlyweb.config']['server_store'][1]
        return store_config['db_config']

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

    def recipe_put(self, recipe):
        srecipe = self._map_srecipe(recipe)
        self.session.merge(srecipe)
        self.session.commit()

    def bag_delete(self, bag):
        try:
            sbag = self.session.query(sBag).filter(sBag.name==bag.name).one()
            self.session.delete(sbag)
            self.session.commit()
        except NoResultFound, exc:
            raise NoBagError('Bag %s not found: %s' % (bag.name, exc))

    def bag_get(self, bag):
        try:
            sbag = self.session.query(sBag).filter(sBag.name == bag.name).one()
            bag = self._map_bag(bag, sbag)

            if not (hasattr(bag, 'skinny') and bag.skinny):
                tiddlers = sbag.tiddlers
                bag.add_tiddlers(Tiddler(tiddler.title) for tiddler in tiddlers)
            return bag
        except NoResultFound, exc:
            raise NoBagError('Bag %s not found: %s' % (bag.name, exc))

    def bag_put(self, bag):
        sbag = self._map_sbag(bag)
        self.session.merge(sbag)
        self.session.commit()

    def tiddler_delete(self, tiddler):
        try:
            stiddler = (self.session.query(sTiddler).
                    filter(sTiddler.title==tiddler.title).
                    filter(sTiddler.bag_name==tiddler.bag).one())
            self.session.delete(stiddler)
            self.session.commit()
            self.tiddler_written(tiddler)
        except NoResultFound, exc:
            raise NoTiddlerError('no tiddler %s to delete, %s' % (tiddler.title, exc))

    def tiddler_get(self, tiddler):
        try:
            stiddler = (self.session.query(sTiddler).
                    filter(sTiddler.title==tiddler.title).
                    filter(sTiddler.bag_name==tiddler.bag).one())
            tiddler = self._map_tiddler(tiddler, stiddler)
            return tiddler
        except NoResultFound, exc:
            raise NoTiddlerError('Tiddler %s not found: %s' % (tiddler.title, exc))

    def tiddler_put(self, tiddler):
        stiddler = self._map_stiddler(tiddler)
        self.session.merge(stiddler)
        self.session.commit()
        self.tiddler_written(tiddler)

    def user_delete(self, user):
        try:
            suser = self.session.query(sUser).filter(sUser.usersign==user.usersign).one()
            self.session.delete(suser)
            self.session.commit()
        except NoResultFound, exc:
            raise NoUserError('user %s not found, %s' % (user.usersign, exc))

    def user_get(self, user):
        try:
            suser = self.session.query(sUser).filter(sUser.usersign==user.usersign).one()
            user = self._map_user(user, suser)
            return user
        except NoResultFound, exc:
            raise NoUserError('user %s not found, %s' % (user.usersign, exc))

    def _map_user(self, user, suser):
        user.usersign = suser.usersign
        user._password = suser.password
        user.note = suser.note
        [user.add_role(role.role_name) for role in suser.roles]
        return user

    def user_put(self, user):
        suser = self._map_suser(user)
        self.session.merge(suser)
        self._map_sroles(user)
        self.session.commit()

    def _map_suser(self, user):
        suser = sUser()
        suser.usersign = user.usersign
        suser.password = user._password
        suser.note = user.note
        return suser

    def _map_sroles(self, user):
        usersign = user.usersign
        for role in user.roles:
            srole = sRole()
            srole.usersign = usersign
            srole.role_name = role
            self.session.merge(srole)

    def list_recipes(self):
        return (self._map_recipe(Recipe(srecipe.name), srecipe) for srecipe in self.session.query(sRecipe).all())

    def list_bags(self):
        return (self._map_bag(Bag(sbag.name), sbag) for sbag in self.session.query(sBag).all())

    def list_users(self):
        return (self._map_user(User(suser.usersign), suser) for suser in self.session.query(sUser).all())

    def list_tiddler_revisions(self, tiddler):
        try:
            stiddler = (self.session.query(sTiddler).
                    filter(sTiddler.title==tiddler.title).
                    filter(sTiddler.bag_name==tiddler.bag).one())
        except NoResultFound, exc:
            raise NoTiddlerError('tiddler %s not found, %s' % (tiddler.title, exc))
        return [revision.revision_id for revision in reversed(stiddler.revisions)]

    def _map_bag(self, bag, sbag):
        bag.desc = sbag.desc
        bag.policy = self._map_policy(sbag.policy)
        return bag

    def _map_policy(self, spolicy):
        policy = Policy()
        policy.owner = spolicy.owner
        for field in Policy.attributes:
            if field == 'owner':
                continue
            setattr(policy, field, self._map_policy_rule(getattr(spolicy, field)))
        return policy

    def _map_policy_rule(self, field_string):
        if field_string:
            field_string = field_string.strip('["').rstrip('"]')
            return field_string.split('","')
        return []

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

    def _map_sbag(self, bag):
        sbag = sBag(bag.name, bag.desc)
        sbag.policy = self._map_spolicy(bag.policy)
        return sbag

    def _map_spolicy(self, policy):
        spolicy = sPolicy()
        spolicy.owner = policy.owner
        for field in Policy.attributes:
            if field == 'owner':
                continue
            setattr(spolicy, field, self._map_spolicy_rule(getattr(policy, field)))
        return spolicy

    def _map_spolicy_rule(self, field_list):
        if field_list:
            field_value = ','.join(['"%s"' % unicode(name) for name in field_list])
            if field_value:
                field_value = '[' + field_value + ']'
            else:
                field_value = None
        else:
            field_value = None
        return field_value

    def _map_srecipe(self, recipe):
        srecipe = sRecipe(recipe.name, recipe.desc)
        srecipe.policy = self._map_spolicy(recipe.policy)
        srecipe.recipe_string = self._map_srecipe_string(recipe)
        return srecipe

    def _map_srecipe_string(self, recipe_list):
        string = u''
        string += '\n'.join(['%s?%s' % (unicode(bag), unicode(filter_string)) for bag, filter_string in recipe_list])
        return string

    def _map_sroles(self, user):
        usersign = user.usersign
        for role in user.roles:
            srole = sRole()
            srole.usersign = usersign
            srole.role_name = role
            self.session.merge(srole)

    def _map_stags(self, tags):
        return self.serializer.serialization.tags_as(tags)

    def _map_stiddler(self, tiddler):
        try:
            stiddler = (self.session.query(sTiddler).
                    filter(sTiddler.title == tiddler.title).
                    filter(sTiddler.bag_name == tiddler.bag).one())
        except NoResultFound:
            stiddler = sTiddler(tiddler.title, tiddler.bag)
            self.session.add(stiddler)

        if tiddler.type and tiddler.type != 'None' and not tiddler.type.startswith('text/'):
            tiddler.text = unicode(b64encode(tiddler.text))

        srevision = sRevision()
        srevision.type = tiddler.type
        srevision.tiddler_id = stiddler.id
        srevision.modified = tiddler.modified
        srevision.modifier = tiddler.modifier
        srevision.text = tiddler.text
        srevision.tags = self._map_stags(tiddler.tags)
        try:
            srevision.revision_id = stiddler.revisions[-1].revision_id + 1
        except IndexError:
            srevision.revision_id = 1

        for field in tiddler.fields:
            if field.startswith('server.'):
                continue
            sfield = sField()
            try:
                sfield.name = self.session.query(sFieldName).filter(sFieldName.name == field).one()
            except NoResultFound:
                name = sFieldName(name=field)
                self.session.add(name)
                sfield.name = name
            sfield.value = tiddler.fields[field]
            sfield.revision_id = srevision.id
            self.session.add(sfield)

        self.session.add(srevision)
        # we need to update the revision on the tiddlyweb tiddler
        # so the correct ETag is set.
        tiddler.revision = srevision.revision_id
        return stiddler

    def _map_tags(self, tags_string):
        return string_to_tags_list(tags_string)

    def _map_tiddler(self, tiddler, stiddler):
        try:
            if tiddler.revision:
                stiddler.rev = tiddler.revision
                revision = stiddler.revision()
            else:
                revision = stiddler.current_revision
            tiddler.modifier = revision.modifier
            tiddler.modified = revision.modified
            tiddler.revision = revision.revision_id
            tiddler.type = revision.type
            if tiddler.type and tiddler.type != 'None' and not tiddler.type.startswith('text/'):
                tiddler.text = b64decode(revision.text.lstrip().rstrip())
            else:
                tiddler.text = revision.text
            tiddler.tags = self._map_tags(revision.tags)

            for sfield in revision.fields:
                tiddler.fields[sfield.name.name] = sfield.value

            tiddler.created = stiddler.created()

            return tiddler
        except IndexError, exc:
            raise NoTiddlerError('No revision %s for tiddler %s, %s' % (stiddler.rev, stiddler.title, exc))

__version__ = '0.2'
