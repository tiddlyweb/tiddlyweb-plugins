instance_tiddlers = {
    '_default_errors': [
        '../src/_errors/index.recipe',
    ]
}


def update_config(config):
    for bag, uris in instance_tiddlers.items():
        config['local_instance_tiddlers'][bag] = uris
