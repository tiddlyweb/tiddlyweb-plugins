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

import logging

IGNORE_PARAMS = []

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

    def search(self, search_query=''):
        full_access = self._determine_user_access()
        open_fields = self.environ[
                'tiddlyweb.config'].get(
                        'mappingsql.open_fields', [])

        query_string, fields = query_dict_to_search_tuple(
                self.environ.get('tiddlyweb.query', {}))

        query = self.session.query(getattr(sTiddler, self.id_column))
        have_query = False

        if query_string:
            if self.environ['tiddlyweb.config'].get('mappingsql.full_text', False):
                query = query.filter(
                                'MATCH(%s) AGAINST(:query in boolean mode)' %
                                ','.join(
                                    self.environ['tiddlyweb.config']
                                    ['mappingsql.default_search_fields'])
                                ).params(query=query_string)
            else:
                query = query.filter(or_(
                            sTiddler.id.like('%%%s%%' % query_string),
                            sTiddler.modifier.like('%%%s%%' % query_string)))
            have_query = True

        for field in fields:
            if not full_access and field not in open_fields:
                continue
            terms = fields[field]
            # TODO: For now we only accept the first term provided
            query = query.filter(getattr(sTiddler, field)==terms[0])
            have_query = True

        if have_query:
            logging.debug('query is: %s' % query)
            limit = self.environ['tiddlyweb.config'].get('mappingsql.limit', 50)
            stiddlers = query.limit(limit).all()
        else:
            stiddlers = []

        bag_name = self.environ['tiddlyweb.config']['mappingsql.bag']
        tiddlers =  (Tiddler(unicode(getattr(stiddler, self.id_column)), bag_name)
                for stiddler in stiddlers)

        return tiddlers


def query_dict_to_search_tuple(original_query_dict):
    query_dict = dict(original_query_dict)
    main_terms = []
    field_terms = {}
    while query_dict:
        keys = query_dict.keys()
        key = keys.pop()
        values = query_dict[key]
        del query_dict[key]
        if key in IGNORE_PARAMS:
            continue

        if key == 'q':
            main_terms.extend([value.lower() for value in values])
        else:
            if key.endswith('_field'):
                prefix = key.rsplit('_', 1)[0]
                value_key = '%s_value' % prefix
                key = values[0].lower().replace(' ', '_')
                try:
                    values = query_dict[value_key]
                    del query_dict[value_key]
                except KeyError:
                    values = []
                if not values:
                    continue
            elif key.endswith('_value'):
                prefix = key.rsplit('_', 1)[0]
                field_key = '%s_field' % prefix
                try:
                    key = query_dict[field_key][0].lower().replace(' ', '_')
                    del query_dict[field_key]
                except KeyError:
                    key = ''
                if not key:
                    continue

            if key == 'avid' and not values[0].isdigit():
                continue

            for value in values:
                try:
                    field_terms[key].append(value.lower())
                except KeyError:
                    field_terms[key] = [value.lower()]
    def quote_term(term):
        if ' ' in term:
            return '"%s"' % term
        return term
    main_terms = [quote_term(term) for term in main_terms]
    return ' '.join(main_terms), field_terms
