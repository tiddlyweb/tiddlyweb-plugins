config = {
        'server_store': ['diststore', {
            'main': ['text', {'store_root': 'store1'}],
            'extras': [
                (r'^b', ['text', {'store_root': 'store2'}]),
                    ],
                }],
        }
