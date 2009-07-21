

from tiddlyweb.filters import FILTER_PARSERS
from tiddlyweb.filters.select import select_parse


MSELECT_SEPARATOR = ','


def mselect(command, tiddlers):
    commands = command.split(MSELECT_SEPARATOR)
    # un_generate the tiddlers so we can use the list multiple times
    tiddlers = list(tiddlers)
    for command in commands:
        func = select_parse(command)
        for tiddler in func(tiddlers):
            yield tiddler
    return


def mselect_parse(command):
    def selector(tiddlers):
        return mselect(command, tiddlers)
    return selector


FILTER_PARSERS['mselect'] = mselect_parse


def init(config):
    pass
