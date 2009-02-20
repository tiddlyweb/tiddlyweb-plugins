"""
A TiddlyWeb plugin for delivering static files.
Very simple at this point. It should handle
caching headers, modification time and the like,
but we don't care about that just yet.

To use this we need to set 'static_dir' in
tiddlywebconfig.py to an absolute or relative
path in which we can find the static files.

And we need to add 'static' to the system_plugins
list.

URL of the files that are found will be
/<static_dir>/filename.
"""

import mimetypes
import os

from tiddlyweb.web.http import HTTP404

DEFAULT_MIME_TYPE = 'application/octet-stream'

def static(environ, start_response):
    pathname = environ['tiddlyweb.config']['static_dir']
    filename = environ['wsgiorg.routing_args'][1]['static_file']

    if '../' in filename:
        raise HTTP404('%s inavlid' % filename)

    full_path = os.path.join(pathname, filename)
    (mime_type, encoding) = mimetypes.guess_type(full_path)
    if not mime_type:
        mime_type = DEFAULT_MIME_TYPE

    if not os.path.exists(full_path):
        raise HTTP404('%s not found' % full_path)

    try:
        static_file = file(full_path)
    except IOError, exc:
        raise HTTP404('%s not found: %s' % (full_path, exc))

    start_response('200 OK', [
        ('Content-Type', mime_type)
        ])

    return static_file


def init(config):
    config['selector'].add('/%s/{static_file:any}' % config['static_dir'], GET=static)
