import mangler
from whoosh.fields import Schema, ID, KEYWORD, TEXT
config = {
        'log_level': 'DEBUG',
        'twanager.tracebacks': True,
        'twanager_plugins': ['tiddlywebplugins.whoosher'],
        'system_plugins': ['tiddlywebplugins.whoosher'],
        }
