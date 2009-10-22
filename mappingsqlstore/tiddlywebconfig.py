config = {
        'log_level': 'DEBUG',
        'server_store': ['mappingsql', {'db_config': 'sqlite:///test.db'}],
        'mappingsql.table': 'test',
        'mappingsql.bag': 'avox',
        'mappingsql.open_fields': ['field_one'],
        # TODO
        #'mappingsql.title_column': 'id',
        }
