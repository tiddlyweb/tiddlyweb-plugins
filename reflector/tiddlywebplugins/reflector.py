"""
A quick plugin to take anything POSTed as a file 
upload on /reflector and reflect it back.
"""

import cgi

from tiddlyweb.web.http import HTTP400

def init(config):
    if 'selector' in config:
        config['selector'].add('/reflector', POST=reflect)


def reflect(environ, start_response):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
    try:
        filehandle = form['file'].file
        type = form['file'].type
        # XXX: this might have charset in it
        #options = form['file'].type_options
    except (AttributeError, ValueError), exc:
        raise HTTP400('Input error: %s', exc)

    start_response('200 OK', [
        ('Content-Type', type)])
    # XXX If reading the file causes an exception
    # it will be trapped as a 500 by HTTPExceptor.
    # Better handling may be desired.
    return filehandle
