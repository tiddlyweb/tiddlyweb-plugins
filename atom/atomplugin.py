"""
A TiddlyWeb plugin that automates the process
of configuring TiddlyWeb to use serializers that
provide Atom feeds of one or more tiddlers, and
links in HTML presentations to those feeds.
"""

EXTENSION_TYPES = {
        'atom': 'application/atom+xml'
        }
SERIALIZERS = {
        'application/atom+xml': ['atom', 'application/atom+xml; charset=UTF-8'],
        'text/html': ['htmlatom', 'text/html; charset=UTF-8']
        }

def init(config):
    config['extension_types'].update(EXTENSION_TYPES)
    config['serializers'].update(SERIALIZERS)
