"""
A reloader for TiddlyWeb when run under CherryPy.

For other servers, like Apache or spawning, you must 
use something else.

This is heavily based on the reloader from Ian Bicking's
Paste. 

This version is modified to exec the server from within
the watcher thread rather than completely exiting.

The exec operation works from a thread on Linux but is not
supported on OS X, so this solution does not work on the Mac.
Contributions for getting it to work on the Mac are welcome. See:

    http://www.cherrypy.org/ticket/581

It has not yet been tested in non-Posix environments.

For related information.

To use this add 'reloader' to system_plugins in tiddlywebconfig.py.

Additional options include 

    'reloader_interval': The number of (floating point) seconds to
                         wait putting checking files. Defaults to 1.
    'reloader_extra_file': A list of other files, besides Python modules
                         to check for modification. Defaults to [].

"""

import os
import sys


def init(config):
    interval = config.get('reloader_interval', 1)
    extra_files = config.get('reloader_extra_files', [])
    install(interval, extra_files)


# (c) 2005 Ian Bicking and contributors; written for Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
"""
A file monitor and server restarter.

Use this like:
"""

import time
import threading

def install(poll_interval=1, extra_files=[]):
    """
    Install the reloading monitor.

    On some platforms server threads may not terminate when the main
    thread does, causing ports to remain open/locked.  The
    ``raise_keyboard_interrupt`` option creates a unignorable signal
    which causes the whole application to shut-down (rudely).
    """
    mon = Monitor(poll_interval=poll_interval, extra_files=extra_files)
    t = threading.Thread(target=mon.periodic_reload)
    t.setDaemon(True)
    t.start()

class Monitor(object):

    instances = []

    def __init__(self, poll_interval, extra_files):
        self.module_mtimes = {}
        self.keep_running = True
        self.poll_interval = poll_interval
        self.extra_files = extra_files
        self.instances.append(self)

    def periodic_reload(self):
        while True:
            if not self.check_reload():
                # use os._exit() here and not sys.exit() since within a
                # thread sys.exit() just closes the given thread and
                # won't kill the process; note os._exit does not call
                # any atexit callbacks, nor does it do finally blocks,
                # flush open files, etc.  In otherwords, it is rude.
                args = [sys.executable] + sys.argv
                os.execv(sys.executable, args)
            time.sleep(self.poll_interval)

    def check_reload(self):
        filenames = list(self.extra_files)
        for module in sys.modules.values():
            try:
                filename = module.__file__
            except (AttributeError, ImportError), exc:
                continue
            if filename is not None:
                filenames.append(filename)
        for filename in filenames:
            try:
                stat = os.stat(filename)
                if stat:
                    mtime = stat.st_mtime
                else:
                    mtime = 0
            except (OSError, IOError):
                continue
            if filename.endswith('.pyc') and os.path.exists(filename[:-1]):
                mtime = max(os.stat(filename[:-1]).st_mtime, mtime)
            elif filename.endswith('$py.class') and \
                    os.path.exists(filename[:-9] + '.py'):
                mtime = max(os.stat(filename[:-9] + '.py').st_mtime, mtime)
            if not self.module_mtimes.has_key(filename):
                self.module_mtimes[filename] = mtime
            elif self.module_mtimes[filename] < mtime:
                print >> sys.stderr, (
                    "%s changed; reloading..." % filename)
                return False
        return True
