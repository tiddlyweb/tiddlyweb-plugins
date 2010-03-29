# A default config, make your own changes here.
import mangler
config = {
    'secret': '8cc3f76b875ab6129f193095a629e0c458380578',
    'twanager_plugins': ['tiddlywebplugins.migrate'],
# this is the store to which we are migrating things
    'target_store': ['text', {'store_root': 'newstore'}],
}
