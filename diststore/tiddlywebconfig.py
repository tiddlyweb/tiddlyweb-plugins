config = {
        'twanager_plugins': ['wserver'],
        'reloader_extra_files': ['diststore.py', 'userbag.py'],
        'server_store': ['diststore', {
            'main': ['text', {'store_root': 'store1'}],
            'extras': [
                (r'^users$', ['userbag', {}]),
                    ],
                }],
        }
