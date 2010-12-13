"""
A quick plugin to take anything POSTed as a file 
upload on /reflector and reflect it back.
"""

import cgi
import urllib2

from tiddlyweb.web.http import HTTP400

def init(config):
    if 'selector' in config:
        config['selector'].add('/reflector', POST=reflect)


def reflect(environ, start_response):
    if environ.get('tiddlyweb.type', '') == 'multipart/form-data':
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
    else:
        # This hack to ensure that we have a uniform interface
        # On the cgi form field values whether we are multipart or
        # url encoded.
        form = cgi.FieldStorage()
        form.list = []
        for key, value in environ['tiddlyweb.query'].items():
            for single_value in value:
                form.list.append(cgi.MiniFieldStorage(key, single_value))
    # Ordering is important here. File will often appear true when
    # it is not.
    if 'uri' in form and form['uri'].value:
        try:
            uri = form.getfirst('uri')
            request = urllib2.Request(uri)
            if (request.get_type() != 'file'):
                filehandle = urllib2.urlopen(uri)
                type = filehandle.info()['content-type']
            else:
                raise ValueError('file: not allowed')
        except (ValueError, AttributeError, urllib2.URLError), exc:
            raise HTTP400('URI Input error: %s' % exc)
    elif 'file' in form and form['file'].file:
        try:
            filehandle = form['file'].file
            type = form['file'].type
            # XXX: this might have charset in it
            #options = form['file'].type_options
        except (AttributeError, ValueError), exc:
            raise HTTP400('File Input error: %s' % exc)
    else:
        raise HTTP400('Incomplete form')

    start_response('200 OK', [
        ('Content-Type', type)])
    # XXX If reading the file causes an exception
    # it will be trapped as a 500 by HTTPExceptor.
    # Better handling may be desired.
    return filehandle
