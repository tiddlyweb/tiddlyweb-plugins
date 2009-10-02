from whoosh.fields import Schema, ID, KEYWORD, TEXT
config = {
        'log_level': 'DEBUG',
        'twanager_plugins': ['whoosher'],
        'system_plugins': ['whoosher'],
        'wsearch.schema': dict(title=TEXT, id=ID(stored=True, unique=True),
            bag=TEXT, text=TEXT, modified=ID, modifier=ID, created=ID,
            tags=TEXT, field_two=TEXT, hello=TEXT),
        }
