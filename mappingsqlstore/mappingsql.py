"""
Fiddle about with mapping an existing sql table to tiddlers.
"""
from sqlalchemy import Table, Column, Unicode, Integer, create_engine, MetaData
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

        if not Store.mapped:
            table_name = self.environ['tiddlyweb.config']['mappingsql.table']
            _tiddlers = Table(table_name, meta,
                        Column('id', Integer, primary_key=True),
                        autoload=True,
                        )
            mapper(sTiddler, _tiddlers)
            Store.mapped = True

    def bag_get(self, bag):
        """Bag will be read only."""
        self._validate_bag_name(bag.name)

        if not (hasattr(bag, 'skinny') and bag.skinny):
            tiddlers = self.session.query(sTiddler.id).all()
            bag.add_tiddlers(Tiddler(unicode(tiddler.id)) for tiddler in tiddlers)
        bag.policy.create = ["NONE"]
        bag.policy.write = ["NONE"]
        bag.policy.delete = ["NONE"]
        bag.policy.manage = ["NONE"]
        return bag

    def tiddler_get(self, tiddler):
        self._validate_bag_name(tiddler.bag)
        try:
            stiddler = self.session.query(sTiddler).filter(
                    sTiddler.id==tiddler.title).one()
        except NoResultFound, exc:
            raise NoTiddlerError('tiddler %s not found, %s' %
                    (tiddler.title, exc))
        # now we need to map the sTiddlers columns to a tiddler
        columns = stiddler.__dict__.keys()
        columns.remove('id')
        for column in columns:
            if column.startswith('_'):
                continue
            if hasattr(tiddler, column):
                setattr(tiddler, column, unicode(getattr(stiddler, column)))
            else:
                tiddler.fields[column] = unicode(getattr(stiddler, column))
	if not tiddler.text:
            tiddler.text = ''
        return tiddler


    def _validate_bag_name(self, name):
        bag_name = self.environ['tiddlyweb.config']['mappingsql.bag']
        if name != bag_name:
            raise NoBagError('Bag %s does not exist' % name)
