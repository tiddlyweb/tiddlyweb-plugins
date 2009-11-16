
import os, sys
from tempfile import NamedTemporaryFile

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.manage import make_command
from tiddlywebplugins.utils import get_store
from tiddlyweb.serializer import Serializer, TiddlerFormatError
from tiddlyweb.store import NoTiddlerError, NoBagError

def init(config_in):
    global config
    config = config_in


@make_command()
def edit(args):
    """Edit a tiddler in a bag in the store. As text. <bag> <tiddler>"""
    try:
        bag, title = args[0:2]
    except IndexError:
        print >> sys.stderr, 'You must provide a bag name and tiddler title'
        sys.exit(1)

    tiddler = Tiddler(title, bag)
    store = get_store(config)
    serializer = Serializer('text')
    serializer.object = tiddler

    #check for bag
    try:
        bagobject = Bag(bag)
        bagobject = store.get(bagobject)
    except NoBagError:
        print >> sys.stderr, 'You must provide the name of a bag that exists.'
        sys.exit(1)


    try:
        tiddler = store.get(tiddler)
        tiddler_content = '%s' % serializer
    except NoTiddlerError:
        tiddler_content = u''


    fd = NamedTemporaryFile(delete=False)
    fd.write(tiddler_content.encode('utf-8'))

    _edit(fd)

    try:
        fd = open(fd.name)
        tiddler_content = fd.read()
        tiddler = serializer.from_string(tiddler_content.decode('utf-8'))
    except (IOError, TiddlerFormatError), exc:
        print 'something went wrong:\n', exc
        print 'your edits are in file %s' % fd.name
        sys.exit(1)

    store.put(tiddler)
    os.unlink(fd.name)

def _edit(fd):
    fd.flush()
    fd.seek(0)
    editor = os.getenv('VISUAL', os.getenv('EDITOR', 'vi'))
    spawned = os.spawnlp(os.P_WAIT, editor, editor, fd.name)
    if spawned != 0:
        print "ERROR"
