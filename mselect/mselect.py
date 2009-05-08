

from tiddlyweb.filters import FILTER_PARSERS
from tiddlyweb.filters.select import select_parse


MSELECT_SEPARATOR = ','


def mselect(command, tiddlers):
    commands = command.split(MSELECT_SEPARATOR)
    results = []
    for command in commands:
        func = select_parse(command)
        results.extend(func(tiddlers))
    return results


def mselect_parse(command):
    def selector(tiddlers):
        return mselect(command, tiddlers)
    return selector


FILTER_PARSERS['mselect'] = mselect_parse


def init(config):
    pass
