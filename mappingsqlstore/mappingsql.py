"""
Fiddle about with mapping an existing sql table to tiddlers.
"""
from sqlalchemy import Table, Column, Unicode, Integer, create_engine, MetaData
from sqlalchemy.sql import or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag
from tiddlyweb.stores import StorageInterface
from tiddlyweb.store import NoBagError, NoTiddlerError

Base = declarative_base()
Session = sessionmaker()

class sTiddler(object):
    pass

class Store(StorageInterface):

    mapped = False

    def __init__(self, environ=None):
        super(Store, self).__init__(environ)
        self._init_store()

    def _init_store(self):
        db_config = self.environ[
                'tiddlyweb.config']['server_store'][1]['db_config']
        engine = create_engine(db_config)
        meta = MetaData()
        meta.bind = engine
        Session.configure(bind=engine)
        self.session = Session()
        self.id_column = self.environ['tiddlyweb.config'].get(
                'mappingsql.id_column', 'id')

        if not Store.mapped:
            id_column = self.environ['tiddlyweb.config'].get(
                    'mappingsql.id_column', 'id')
            table_name = self.environ['tiddlyweb.config']['mappingsql.table']
            _tiddlers = Table(table_name, meta,
                        Column(self.id_column, Integer, primary_key=True),
                        autoload=True,
                        )
            mapper(sTiddler, _tiddlers)
            Store.mapped = True

    def bag_get(self, bag):
        """Bag will be read only."""
        self._validate_bag_name(bag.name)

        if not (hasattr(bag, 'skinny') and bag.skinny):
            stiddlers = self.session.query(
                    getattr(sTiddler, self.id_column)).all()
            bag.add_tiddlers(Tiddler(
                unicode(getattr(stiddler, self.id_column)))
                for stiddler in stiddlers)
        bag.policy.create = ["NONE"]
        bag.policy.write = ["NONE"]
        bag.policy.delete = ["NONE"]
        bag.policy.manage = ["NONE"]
        return bag

    def tiddler_get(self, tiddler):
        full_access = self._determine_user_access()
        open_fields = self.environ[
                'tiddlyweb.config'].get(
                        'mappingsql.open_fields', [])

        self._validate_bag_name(tiddler.bag)
        try:
            stiddler = self.session.query(sTiddler).filter(
                    getattr(sTiddler, self.id_column)==tiddler.title).one()
        except NoResultFound, exc:
            raise NoTiddlerError('tiddler %s not found, %s' %
                    (tiddler.title, exc))
        # now we need to map the sTiddlers columns to a tiddler
        columns = stiddler.__dict__.keys()
        columns.remove(self.id_column)
        for column in columns:
            if column.startswith('_'):
                continue
            if not full_access and column not in open_fields:
                continue
            if hasattr(tiddler, column):
                setattr(tiddler, column, unicode(getattr(stiddler, column)))
            else:
                tiddler.fields[column] = unicode(getattr(stiddler, column))
	if not tiddler.text:
            tiddler.text = ''
        return tiddler

    def _determine_user_access(self):
        """
        For now we return true if the user is authenticated.
        """
        try:
            current_user = self.environ['tiddlyweb.usersign']
        except KeyError:
            return False
        if current_user['name'] != u'GUEST':
            return True
        return False

    def _validate_bag_name(self, name):
        bag_name = self.environ['tiddlyweb.config']['mappingsql.bag']
        if name != bag_name:
            raise NoBagError('Bag %s does not exist' % name)

    def search(self, search_query):
        print search_query
        query_string, fields = self._parse_query(search_query)
        if self.environ['tiddlyweb.config'].get('mappingsql.full_text', False):
            stiddlers = self.session.query(
                    getattr(sTiddler, self.id_column)).filter(
                            'MATCH(%s) AGAINST(:query in boolean mode)' %
                            self.environ['tiddlyweb.config']['mappingsql.default_search_fields']
                            ).params(query=query_string)
        else:
            query = self.session.query(
                    getattr(sTiddler, self.id_column)).filter(or_(
                        sTiddler.id.like('%%%s%%' % query_string),
                        sTiddler.modifier.like('%%%s%%' % query_string)))
        for field in fields:
            query = query.filter(getattr(sTiddler, field)==fields[field])
        print query
        stiddlers = query.all()
        tiddlers =  (Tiddler(unicode(getattr(stiddler, self.id_column)))
                for stiddler in stiddlers)
        return tiddlers

    def _parse_query(self, query):
        # todo: deal with quotes
        pieces = query.split()
        query_strings = []
        fields = {}
        for piece in pieces:
            if ':' in piece:
                key, value = piece.split(':', 1)
                fields[key] = value
            else:
                query_strings.append(piece)
        query_string = ' '.join(query_strings)
        return query_string, fields
