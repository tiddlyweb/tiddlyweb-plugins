config = {
        'log_level': 'DEBUG',
        'server_store': ['tiddlywebplugins.mappingsql',
            {'db_config': 'sqlite:///test.db'}],
        'mappingsql.table': 'test',
        'mappingsql.bag': 'avox',
        'mappingsql.open_fields': ['field_one'],
        'mappingsql.default_search_fields': ['id', 'modifier'],
        # TODO
        #'mappingsql.title_column': 'id',
        }
