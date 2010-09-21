"""
Provide an mselect filter type. This extends the filter syntax
to allow a union of two or more select type filters in one
filter step. This allows for union or multiple type selections.
The following example will select those tiddlers which have tag
blog OR tag published and then sort by modified time:

        mselect=tag:blog,tag:published;sort=-modified

Install by adding 'tiddlywebplugins.mselect' to 'system_plugins'
in tiddlywebconfig.py.
"""

from tiddlyweb.filters import FILTER_PARSERS
from tiddlyweb.filters.select import _get_entity


OOM_SEPARATOR = ','

test_oom = None


def init(config):

    global test_oom

    def select_if_one(attribute, value, entities, environ=None):
        if environ == None:
            environ = {}

        store = environ.get('tiddlyweb.store', None)

        if environ:
            try:
                separator = environ['tiddlyweb.config']['oom.separator']
            except (TypeError, KeyError):
                separator = OOM_SEPARATOR
        else:
            separator = config.get('oom.separator', OOM_SEPARATOR)

        values = value.split(separator)

        def get_value(entity, attribute):
            try:
                return getattr(entity, attribute)
            except AttributeError:
                try:
                    return entity.fields[attribute]
                except (AttributeError, KeyError):
                    return None

        return (entity for entity in entities if
                get_value(_get_entity(entity, store), attribute) in values)
        

    def oom_parse(command):
        attribute, args = command.split(':', 1)
        def selector(entities, indexable=False, environ=None):
            return select_if_one(attribute, args, entities, environ=environ)
        return selector

    FILTER_PARSERS['oom'] = oom_parse

    test_oom = select_if_one
