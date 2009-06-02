# Sample config for multistore.
#
# There can be as many readers and writers as desired.
#
# If there are multiple readers, all readers are read, 
# but the content returned comes from the last reader.
#
# The items in the readers and writers lists are formatter
# exactly the same as server_store: A two item list with
# the first item being a string that names the module that
# has the StorageInterface implementation, the second being
# a dictionary with whatever configuration information is
# required for the named store.
#
config = {
        'server_store': ['multistore', {
            'writers': [
                ['text', {'store_root': 'store1'}],
                ['text', {'store_root': 'store2'}],
                ],
            'readers': [
                ['text', {'store_root': 'store2'}],
                ],
            }],
        'log_level': 'DEBUG',
        }
