config = {
        'server_store': ['diststore', {
            'main': ['text', {'store_root': 'store'}],
            'extras': [
                (r'^users$', ['userbag', {}]),
                    ],
                }],
        }
