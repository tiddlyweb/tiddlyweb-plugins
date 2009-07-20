"""
A twanager plugin which provides the same job as 
the reloader.py but uses multiple process to do the
watching, rather than threads, thus getting around 
problems on some architectures.
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
    """Run a server that reloads code."""
    poll_interval = config.get('reloader_interval', 1)
    extra_files = config.get('reloader_extra_files', [])
    pid = os.fork()
    load_app() # we must call load_app() to process plugins and handlers
    if pid:
        signal.signal(signal.SIGCHLD, sig_child_handler(pid))
        mon = ForkingMonitor(poll_interval=poll_interval, extra_files=extra_files)
        mon.pid = pid
        mon.args = args
        mon.periodic_reload()
    _run_server(args)


def sig_child_handler(pid):
    def _sig_child_handler(signum, frame):
        print >> sys.stderr, 'Child server process at %s sent %s.' % (pid, signum)
        try:
            os.waitpid(-1, os.WNOHANG)
        except OSError:
            print "waiting didn't work"
            pass
    return _sig_child_handler


def _run_server(args):
    server(args)


class ForkingMonitor(Monitor):

    def periodic_reload(self):
        while True:
            if not self.check_reload():
                os.kill(self.pid, signal.SIGTERM)
                args = [sys.executable] + sys.argv
                args.insert(args.index('wserver'), 'server')
                args.remove('wserver')
                pid = os.spawnv(os.P_NOWAIT, sys.executable, args)
                self.pid = pid
            time.sleep(self.poll_interval)
