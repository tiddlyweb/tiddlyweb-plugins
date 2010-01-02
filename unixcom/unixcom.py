"""
Twanager commands that mimic unix command.
"""

import sys

from tiddlyweb.manage import make_command, usage
from tiddlyweb.commands import ltiddlers
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler, current_timestring
from tiddlyweb.store import NoBagError, NoTiddlerError
from tiddlywebplugins.utils import get_store

def init(config_in):
    global config
    config = config_in

@make_command()
def mv(args):
    """move a tiddler from one bag to another, maybe renaming: <s bag> <tiddler> <t bag> [tiddler]"""
    source_bag, source_tiddler, target_bag, target_tiddler = _parse_args(args, 3, 4)
    original_tiddler_title = source_tiddler
    original_bag_name = source_bag

    source_tiddler, target_tiddler = _reify_entities(source_bag,
            source_tiddler, target_bag, target_tiddler)

    _write_new_tiddler(source_tiddler, target_tiddler)
    _delete_tiddler(original_bag_name, original_tiddler_title)


@make_command()
def rm(args):
    """remove a tiddler from a bag: <bag> <tiddler>"""
    source_bag, source_tiddler = _parse_args(args, 2, 2)
    source_tiddler = _reify_entities(source_bag, source_tiddler)
    _delete_tiddler(source_tiddler.bag, source_tiddler.title)


@make_command()
def cp(args):
    """copy a tiddler from one bag to another, maybe renaming: <s bag> <tiddler> <t bag> [tiddler]"""
    source_bag, source_tiddler, target_bag, target_tiddler = _parse_args(args, 3, 4)
    original_tiddler_title = source_tiddler
    original_bag_name = source_bag

    source_tiddler, target_tiddler = _reify_entities(source_bag,
            source_tiddler, target_bag, target_tiddler)

    _write_new_tiddler(source_tiddler, target_tiddler)


@make_command()
def touch(args):
    """create a new empty tiddler or update modfied time on existing tiddler: <bag> <tiddler>"""
    source_bag, source_tiddler = _parse_args(args, 2, 2)
    source_tiddler = _reify_entities(source_bag, source_tiddler, source_exist=False)
    source_tiddler.modified = current_timestring()
    _write_new_tiddler(source_tiddler)

@make_command()
def ls(args):
    """List all the tiddlers on the system. [<bag> <bag> <bag>] to limit."""
    ltiddlers(args)

def _delete_tiddler(bagname, tiddlertitle):
    # remove the previous tiddler
    old_tiddler = _get_tiddler(bagname, tiddlertitle)
    store = get_store(config)
    store.delete(old_tiddler)


def _write_new_tiddler(source_tiddler, target_tiddler=None):
    # reset the source tiddler as the target tiddler (so its contents
    # are saved
    source_tiddler.revision = 0
    if target_tiddler:
        source_tiddler.title = target_tiddler.title
        source_tiddler.bag = target_tiddler.bag
    store = get_store(config)
    store.put(source_tiddler)


def _reify_entities(source_bag, source_tiddler, target_bag=None, target_tiddler=None,
        source_exist=True):
    try:
        source_bag = _get_bag(source_bag)
        source_tiddler = _get_tiddler(source_bag.name, source_tiddler)
    except NoBagError:
        print >> sys.stderr, 'Bag %s does not exist. It must.' % source_bag
        usage()
    except NoTiddlerError:
        if source_exist:
            print >> sys.stderr, 'Tiddler %s does not exist. It must.' % source_tiddler
            usage()
        else:
            return Tiddler(source_tiddler, source_bag.name)

    if target_bag:
        try:
            target_bag = _get_bag(target_bag)
            if target_tiddler:
                try:
                    target_tiddler = _get_tiddler(target_bag.name, target_tiddler)
                except NoTiddlerError:
                    target_tiddler = Tiddler(target_tiddler, target_bag.name)
            else:
                target_tiddler = Tiddler(source_tiddler.title, target_bag.name)
        except NoBagError:
            print >> sys.stderr, 'Bag %s does not exist. It must.' % target_bag
            usage()

        return source_tiddler, target_tiddler
    else:
        return source_tiddler


def _get_bag(bagname):
    store = get_store(config)
    bag = Bag(bagname)
    return store.get(bag)


def _get_tiddler(bagname, tiddlertitle):
    store = get_store(config)
    tiddler = Tiddler(tiddlertitle, bagname)
    return store.get(tiddler)


def _parse_args(args, required, optional):
    if len(args) == optional:
        print args
        return args
    elif len(args) == required:
        args.extend([None for i in range(optional-required)])
        print args
        return args
    else:
        print >> sys.stderr, '%s args required, %s with options' % (required, optional)
        usage()
