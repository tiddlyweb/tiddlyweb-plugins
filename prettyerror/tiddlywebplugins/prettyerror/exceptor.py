"""
Provide a PrettyHTTPExceptor class which can be used to
replace the HTTPExceptor.
"""

import sys
import string
import traceback
import logging

from itertools import chain

from tiddlyweb.web.http import HTTPExceptor, HTTPException
from tiddlyweb.control import determine_bag_from_recipe
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import NoRecipeError, NoBagError, NoTiddlerError

DEFAULT_TEXT = """
<html>
<head><title>Error: $status</title></head>
<body>
<p>There was a $status error with the following message:</p>
    <blockquote>$message</blockquote>
<p>There was also an error retrieving the error tiddler for
this message.</p>
</body>
</html>
"""


class PrettyHTTPExceptor(HTTPExceptor):
    """
    Subclass HTTPExceptor to change error reporting from
    simple text/plain messages provided by the exceptions
    to text/html messages provided by tiddlers with titles
    the same as the HTTP status involved. The tiddler.text
    is a template with $name style variable interpolation.
    The names come from the exception status, the exception
    message, and any key in the environment. For keys in 
    the environment that have dict values, composite keys are
    created making a flat dict:
    environ['tiddlyweb.config']['server_host']['host'] becomes
    tiddlyweb_config_server_host_host

    Tiddlers are retrieved from a recipe defined in configuration
    as 'prettyerror.recipe', defaulting to '_errors'.

    If not matching tiddler can be found one with the title
    'default' is used. If not default is available then
    a DEFAULT_TEXT string is used.
    """

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
        """
        Change the content-type header to text/html, load up the
        relevant error tiddler, format its contents, and send out
        the text.
        """
        status = exc.status.split(' ', 1)[0]
        output = exc.output()

        headers = []
        for header, value in exc.headers():
            if (not status.startswith('3') and
                    header.lower() == 'content-type'):
                value = 'text/html; charset=UTF-8'
            headers.append((header, value))

        start_response(exc.status, headers, exc_info)

        # don't send pretty errors with 3xx responses
        if not status.startswith('3') and output:
            status_tiddler = self._get_status_tiddler(environ, status)
            text = format_error_tiddler(environ, status_tiddler, exc)
        elif output:
            return output
        else:
            text = ''

        return [text]

    def _get_status_tiddler(self, environ, status):
        """
        Load up the tiddler associated with the current status.
        If the tiddler is not present in the recipe, load up
        the tiddler with title 'default'. If that tiddler is
        not present, use DEFAULT_TEXT.
        """
        try:
            store = environ['tiddlyweb.store']
            recipe_name = environ['tiddlyweb.config'].get('prettyerror.recipe',
                    '_errors')
            tiddler = Tiddler(status)
            recipe = Recipe(recipe_name)
            recipe = store.get(recipe)
            bag = determine_bag_from_recipe(recipe, tiddler, environ)
            tiddler.bag = bag.name
            tiddler = store.get(tiddler)
        except (NoRecipeError, NoBagError):
            if status == 'default':
                tiddler.text = DEFAULT_TEXT
            else:
                tiddler = self._get_status_tiddler(environ, 'default')
        except (NoTiddlerError):
            # If there is no default tiddler we get recursion error.
            tiddler = self._get_status_tiddler(environ, 'default')
        except:  # Deal with failures early in the stack
            tiddler.text = DEFAULT_TEXT

        return tiddler


def flattendict(d, pfx='', sep='_'):
    """
    Flatten a dictionary making descendent keys parts of the keys
    with a _ separator.
    """
    def tidy_key(key):
        key = key.replace('.', '_')
        key = key.replace('/', '_')
        try:
            return key.encode('utf8')
        except UnicodeEncodeError:
            return key
    if isinstance(d, dict):
        if pfx:
            pfx += sep
        return chain(*(flattendict(v, pfx+tidy_key(k), sep)
            for k, v in d.iteritems()))
    else:
        return (pfx, d),


def format_error_tiddler(environ, status_tiddler, exc):
    """
    Use the text from the provided tiddler as a Template, passing
    in the exception info and the current environment as keywords
    for the template.
    """
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
    info.update(flattendict(environ))

    return template.substitute(**info)
