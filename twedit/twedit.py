
import os, sys
from tempfile import NamedTemporaryFile

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.manage import make_command
from tiddlywebplugins import get_store
from tiddlyweb.serializer import Serializer, TiddlerFormatError

def init(config_in):
    global config
    config = config_in


@make_command()
def edit(args):
    """Edit a tiddler in a big in the store. As text."""
    try:
        title, bag = args[0:2]
    except IndexError:
        print >> sys.stderr, 'You must provide a tiddler title and bag name'

    tiddler = Tiddler(title, bag)
    store = get_store(config)
    tiddler = store.get(tiddler)

    serializer = Serializer('text')
    serializer.object = tiddler

    fd = NamedTemporaryFile(delete=False)
    tiddler_content = '%s' % serializer
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
