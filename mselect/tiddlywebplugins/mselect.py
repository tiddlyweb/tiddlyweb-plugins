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
from tiddlyweb.util import merge_config
DEFAULT_ENVIRON = {"tiddlyweb.config":{"mselect.separator":","}}

def mselect(command, tiddlers,environ=DEFAULT_ENVIRON):
    commands = command.split(environ['tiddlyweb.config']['mselect.separator'])
    # un_generate the tiddlers so we can use the list multiple times
    tiddlers = list(tiddlers)
    for command in commands:
        func = select_parse(command)
        for tiddler in func(tiddlers):
            yield tiddler
    return

def mselect_parse(command):
    def selector(tiddlers, indexable=False, environ=DEFAULT_ENVIRON):
        return mselect(command, tiddlers,environ)
    return selector
    
def init(config):
    merge_config(config,{"mselect.separator":"|"})
    FILTER_PARSERS['mselect'] = mselect_parse
