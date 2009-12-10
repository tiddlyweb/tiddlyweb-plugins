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
        # plugins
        'system_plugins': ['tiddlywebwiki'],
        # how are we storing data
        'server_store': ['googledata', {}],
        # how do we extract user information from requests
        'extractors': ['google_user_extractor'],
        # how do we authenticate (if needed)
        'auth_systems': ['google_user_challenger'],
        # where is a handy css file located
        'css_uri': '/static/tiddlyweb.css',
        # what is the host and port of our server
        'server_host': server_host,
        'log_level': 'DEBUG',
        }
