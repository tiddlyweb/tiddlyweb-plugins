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

# XXX: make the function available for testing.
# This enclosure mess works around some bugs in
# control.filter_tiddlers_from_bag which are fixed in 
# TiddlyWeb 1.1
test_mselect = None

def init(config):

    global test_mselect

    def mselect(command, tiddlers, environ=None):
        global separator
        if environ:
            try:
                separator = environ['tiddlyweb.config']['mselect.separator']
            except (TypeError, KeyError):
                separator = MSELECT_SEPARATOR
        else:
            separator = config.get('mselect.separator', MSELECT_SEPARATOR)
        commands = command.split(separator)
        # un_generate the tiddlers so we can use the list multiple times
        tiddlers = list(tiddlers)
        seen_tiddlers = []
        for command in commands:
            func = select_parse(command)
            for tiddler in func(tiddlers):
                if tiddler not in seen_tiddlers:
                    yield tiddler
                seen_tiddlers.append(tiddler)
        return

    def mselect_parse(command):
        def selector(tiddlers, indexable=False, environ={}):
            return mselect(command, tiddlers, environ)
        return selector

    FILTER_PARSERS['mselect'] = mselect_parse

    test_mselect = mselect
