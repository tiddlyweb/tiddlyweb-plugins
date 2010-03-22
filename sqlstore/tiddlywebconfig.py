config = {
        'server_store': ['sql2', {'db_config': 'sqlite:///store.db'}],
        'system_plugins': ['tiddlywebwiki'],
        'twanager_plugins': ['tiddlywebwiki'],
        'sqlsearch.main_fields': [u'tiddlers.title', u'revisions.text', u'fields:huntsman', u'fields:target'],
        'sqlsearch.order_field': [u'fields:huntsman'], # XXX not currently in use
        'log_level': 'DEBUG',
        }
