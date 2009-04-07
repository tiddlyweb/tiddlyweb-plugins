import os

# The following block determine the server host
# setting. This allows us to work local and on
# GAE without changing config by hand.
if os.environ['SERVER_SOFTWARE'].startswith('Dev'):
    server_host = {
            'scheme': 'http',
            'host': 'localhost',
            'port': '8000',
            }
else:
    server_host = {
            'scheme': 'http',
            'host': 'tiddlyweb.appspot.com',
            'port': '80',
            }

config = {
        # how are we storing data
        'server_store': ['googledata', {}],
        # what extensions (on urls) can we use in addition
        # to defaults
        'extension_types': {
            'atom': 'application/atom+xml',
            },
        # which serializers are used to handle particular
        # content types (merged with defauls)
        'serializers': {
            'application/atom+xml': ['atom.atom', 'application/atom+xml; charset=UTF-8'],
            'text/html': ['atom.htmlatom', 'text/html; charset=UTF-8'],
            },
        # how do we extract user information from requests
        'extractors': ['google_user_extractor'],
        # how do we authenticate (if needed)
        'auth_systems': ['google_user_challenger'],
        # where is a handy css file located
        'css_uri': '/static/tiddlyweb.css',
        # what is the host and port of our server
        'server_host': server_host,
        }
