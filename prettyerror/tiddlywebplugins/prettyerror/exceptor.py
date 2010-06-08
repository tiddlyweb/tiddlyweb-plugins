"""
Override the HTTPExceptor with one that delivers tiddlers
containing error messages.
"""

import sys
import string
import traceback
import logging

from tiddlyweb.web.http import HTTPExceptor, HTTPException
from tiddlyweb.control import determine_bag_from_recipe
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import NoRecipeError, NoBagError, NoTiddlerError

DEFAULT_TEXT = """
<html>
<head><title>Error: $status</title></head>
<body>
<p>There was a $status error with the following message:
    <blockquote>$message</blockquote>
There was also an error retrieving the error tiddler for 
this message.
</p>
</body>
</html>
"""


class PrettyHTTPExceptor(HTTPExceptor):

    def __call__(self, environ, start_response, exc_info=None):
        try:
            return self.application(environ, start_response)
        except HTTPException, exc:
            return self._send_response(environ, start_response, exc_info, exc)
        except:
            etype, value, traceb = sys.exc_info()
            exception_text = ''.join(traceback.format_exception(
                etype, value, traceb, None))
            print >> environ['wsgi.errors'], exception_text
            logging.warn(exception_text)

            exc = HTTPException(exception_text)
            exc.status = '500 server error'
            return self._send_response(environ, start_response,
                    sys.exc_info(), exc)

    def _send_response(self, environ, start_response, exc_info, exc):
        headers = []
        for header, value in exc.headers():
            if header.lower() == 'content-type':
                value = 'text/html; charset=UTF-8'
            headers.append((header, value))
        status = exc.status.split(' ', 1)[0]
        status_tiddler = self._get_status_tiddler(environ, status)
        start_response(exc.status, headers, exc_info)
        if exc.output():
            text = self._format_tiddler(environ, status_tiddler, exc)
        else:
            text = ''
        return [text]

    def _format_tiddler(self, environ, status_tiddler, exc):
        template = string.Template(status_tiddler.text.encode('UTF-8'))
        info = {'status': exc.status, 'message': ''.join(exc.output())}
        if not environ['SCRIPT_NAME'] and environ['PATH_INFO']:
            environ['SCRIPT_NAME'] = environ['PATH_INFO']
        css_uri = environ['tiddlyweb.config'].get('css_uri', None)
        info['css_link'] = ''
        if css_uri:
            info['css_link'] = """<link
rel="stylesheet"
href="%s"
type="text/css" />""" % css_uri
        info.update(environ)
        return template.substitute(**info)

    def _get_status_tiddler(self, environ, status):
        store = environ['tiddlyweb.store']
        recipe_name = environ['tiddlyweb.config'].get('prettyerror.recipe',
                '_errors')
        tiddler = Tiddler(status)
        try:
            recipe = Recipe(recipe_name)
            recipe = store.get(recipe)
            bag = determine_bag_from_recipe(recipe, tiddler, environ)
            tiddler.bag = bag.name
            tiddler = store.get(tiddler)
        except (NoRecipeError, NoBagError), exc:
            if status == 'default':
                tiddler.text = DEFAULT_TEXT
            else:
                tiddler = self._get_status_tiddler(environ, 'default')
        except (NoTiddlerError), exc:
            # If there is no default tiddler we get recursion error.
            tiddler = self._get_status_tiddler(environ, 'default')

        return tiddler

