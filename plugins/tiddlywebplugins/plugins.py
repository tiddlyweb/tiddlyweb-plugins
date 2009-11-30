
import logging

def init(config):
    extend_plugins(config)


def extend_plugins(config):
    plugin_file = config.get('plugin_file', 'extra_plugins')
    try:
        plugins = [line.strip() for line in open(plugin_file).readlines()
                if not line.startswith('#')]
    except IOError, exc:
        logging.warning('unable to read extra plugins file: %s' % exc)
        plugins = []

    config['system_plugins'].extend(plugins)

    print config
