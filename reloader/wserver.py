"""
A twanager plugin which provides the same job as 
the reloader.py but uses multiple process to do the
watching, rather than threads, thus getting around 
problems on some architectures (notably OS X).
"""

from tiddlyweb.manage import make_command, server
from tiddlyweb.web.serve import load_app

from reloader import Monitor

import os
import signal
import sys
import time

def init(config_in):
    global config
    config = config_in


@make_command()
def wserver(args):
    """Run a server that reloads code automagically."""
    poll_interval = config.get('reloader_interval', 1)
    extra_files = config.get('reloader_extra_files', [])
    pid = _start_server()
    if pid:
        # we must call load_app() to process system_plugins and handlers
        # and get them into sys.modules, which is what the Monitor
        # watches.
        load_app()
        signal.signal(signal.SIGCHLD, sig_child_handler(pid))
        mon = ForkingMonitor(poll_interval=poll_interval, extra_files=extra_files)
        mon.pid = pid
        mon.periodic_reload()


def sig_child_handler(pid):
    # This tries to make sure we don't leave behind zombies.
    # BWAINS!!!
    def _sig_child_handler(signum, frame):
        print >> sys.stderr, 'Child server process at %s sent %s.' % (pid, signum)
        try:
            os.waitpid(-1, os.WNOHANG)
        except OSError:
            print "waiting didn't work"
            pass
    return _sig_child_handler


def _start_server():
    """
    Spawn a twanager server process with the same arguments
    twanager wserver was started with.
    """
    args = [sys.executable] + sys.argv
    args.insert(args.index('wserver'), 'server')
    args.remove('wserver')
    pid = os.spawnv(os.P_NOWAIT, sys.executable, args)
    return pid


class ForkingMonitor(Monitor):
    """
    Subclass of reloader.Monitor that replaces periodic_reloader
    with a call to spawn a different server, rather than execing
    an entire new process.
    """

    def periodic_reload(self):
        while True:
            if not self.check_reload():
                # We've been told we need to reload.
                # Kill the child server and start a new one.
                os.kill(self.pid, signal.SIGTERM)
                pid = _start_server()
                self.pid = pid
            time.sleep(self.poll_interval)
