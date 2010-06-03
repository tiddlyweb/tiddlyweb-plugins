
store_contents = {}
store_structure = {}

store_contents['_default_errors'] = [
        'src/_errors/index.recipe',
        ]

store_structure['recipes'] = {}
store_structure['bags'] = {}

store_structure['recipes']['_errors'] = {
        'desc': 'Pretty Errors Error Tiddlers',
        'recipe': [
            ('_default_errors', ''),
            ('_errors', ''),
            ],
        'policy': {
            'read': [],
            'write': ['R:ADMIN'],
            'manage': ['R:ADMIN'],
            'delete': ['R:ADMIN'],
            'owner': 'administractor',
            'write': ['R:ADMIN'],
            },
        }

store_structure['bags']['_default_errors'] = {
        'desc': 'Default error tiddlers for Pretty Errors',
        'policy': {
            'read': [],
            'write': ['NONE'],
            'create': ['NONE'],
            'delete': ['NONE'],
            'manage': ['NONE'],
            'accept': ['NONE'],
            'owner': 'administrator',
            },
        }

store_structure['bags']['_errors'] = {
        'desc': 'Override error tiddlers for Pretty Errors',
        'policy': {
            'read': [],
            'write': ['R:ADMIN'],
            'create': ['R:ADMIN'],
            'delete': ['R:ADMIN'],
            'manage': ['R:ADMIN'],
            'accept': ['NONE'],
            'owner': 'administrator',
            },
        }

instance_config = {
        'system_plugins': ['tiddlywebplugins.prettyerror']
        }
