# Modified version of paste.gzipper which includes the following copyright
# information.
# (c) 2005 Ian Bicking and contributors; written for Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php

"""
WSGI middleware

Gzip-encodes the response.
"""

import gzip

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class Gzipper(object):

    def __init__(self, application, compress_level=6):
        self.application = application
        self.compress_level = int(compress_level)

    def __call__(self, environ, start_response):
        if 'gzip' not in environ.get('HTTP_ACCEPT_ENCODING', ''):
            # nothing for us to do, so this middleware will
            # be a no-op:
            return self.application(environ, start_response)
        def replacement_start_response(status, headers, exc_info=None):
            _remove_header(headers, 'content-length')
            headers.append(('content-encoding', 'gzip'))
            return start_response(status, headers, exc_info)

        app_iter = self.application(environ, replacement_start_response)

        buffer = StringIO()
        gzipped = gzip.GzipFile(mode='wb', compresslevel=self.compress_level, fileobj=buffer)

        for s in app_iter:
            gzipped.write(s)
        gzipped.close()

        buffer.seek(0)
        s = buffer.getvalue()
        buffer.close()

        print s
        return [s]


def _remove_header(headers, name):
    name = name.lower()
    i = 0
    result = None
    while i < len(headers):
        if headers[i][0].lower() == name:
            result = headers[i][1]
            del headers[i]
            continue
        i += 1
    return result

# You will need the following tiddlywebconfig.py (or a 
# derivation thereof.
# from gzipper import Gzipper
# from tiddlyweb.web.http import HTTPExceptor
# from tiddlyweb.web.wsgi import StoreSet, EncodeUTF8, SimpleLog, HTMLPresenter, PermissionsExceptor
# 
# config = {
#         'server_response_filters': [
#             HTMLPresenter,
#             PermissionsExceptor,
#             HTTPExceptor,
#             EncodeUTF8,
#             SimpleLog,
#             Gzipper
#             ],
#         }
