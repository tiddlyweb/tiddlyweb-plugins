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
from tiddlyweb.filters.select import select_parse


MSELECT_SEPARATOR = ','


def mselect(command, tiddlers, environ=None):
    if environ == None:
        environ = {}
    config = environ.get('tiddlyweb.config', {})
    separator = config.get('mselect.separator', MSELECT_SEPARATOR)
    commands = command.split(separator)
    # un_generate the tiddlers so we can use the list multiple times
    tiddlers = list(tiddlers)
    for command in commands:
        func = select_parse(command)
        for tiddler in func(tiddlers):
            yield tiddler
    return


def mselect_parse(command):
    def selector(tiddlers, indexable=False, environ={}):
        return mselect(command, tiddlers, environ)
    return selector


FILTER_PARSERS['mselect'] = mselect_parse


def init(config):
    pass
