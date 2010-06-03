"""
Used for testing only.
"""

from tiddlywebplugins.instancer.util import get_tiddler_locations
from tiddlywebplugins.prettyerror.instance import store_contents

config = {
        'instance_tiddlers': get_tiddler_locations(
            store_contents, 'tiddlywebplugins.prettyerror'),
        'log_level': 'DEBUG',
        }
