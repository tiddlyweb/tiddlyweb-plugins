import os

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
        'server_store': ['googledata', {}],
        'extension_types': {
            'atom': 'application/atom+xml',
            },
        'serializers': {
            'application/atom+xml': ['atom.atom', 'application/atom+xml; charset=UTF-8'],
            'text/html': ['atom.htmlatom', 'text/html; charset=UTF-8'],
            },
        'extractors': ['google_user_extractor'],
        'auth_systems': ['google_user_challenger'],
        'css_uri': '/static/tiddlyweb.css',
        #'system_plugins': ['twoter'],
        'server_host': server_host,
        }
