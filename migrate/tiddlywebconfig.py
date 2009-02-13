# A default config, make your own changes here.
config = {
    'secret': '8cc3f76b875ab6129f193095a629e0c458380578',
    'twanager_plugins': ['migrate'],
# this is the store to which we are migrating things
    'target_store': ['simpletext', {'store_root': 'newstore'}],
}
