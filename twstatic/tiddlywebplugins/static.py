"""
A TiddlyWeb plugin for delivering static files.
Very simple at this point. It ought to handle
caching headers, modification time and the like,
but thus far it does not. Please provide patches
if you make those sorts of changes.

To use this set 'static_file_dir' in tiddlywebconfig.py to
an absolute or relative (to the instance) path in
which we can find the static files. If you do not set it
a default of 'static' (relative to the current dir) will
be used.

You also need to set 'static_url_dir' in tiddlywebconfig.py
to a url path relative to the base or your tiddlyweb URL
space. server_prefix and '/' will be prepended to the path.
If you do not set static_url_dir, then 'static' will be used.

Add 'static' to the system_plugins list.

The URL of the static files will be

  <server_prefix>/<static_url_dir>/<filename>

<filename> may include path separators, allowing you to have
directories in your 'static_file_dir'

Here is sample configuration to put in tiddlywebconfig.py

    config = {
            'css_uri': '/stuff/html/tiddlyweb.css',
            'system_plugins': ['tiddlywebplugins.static'],
            'static_url_dir': 'stuff/html',
            'static_file_dir': '/home/foobar/mystuff',
            'log_level': 'DEBUG',
            }
"""

import mimetypes
import os

from httpexceptor import HTTP404

DEFAULT_MIME_TYPE = 'application/octet-stream'

def static(environ, start_response):
    pathname = environ['tiddlyweb.config'].get('static_file_dir', 'static')
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
    url_path = config.get('static_url_dir', 'static')
    config['selector'].add('/%s/{static_file:any}' % url_path, GET=static)
