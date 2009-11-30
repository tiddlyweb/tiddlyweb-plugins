
import logging
import urlparse
import os.path
from tiddlyweb.manage import make_command, usage, info as manage_info

twanager_config = {}

def init(config_in):
    if 'selector' in config_in:
        extend_plugins(config_in)
    else:
        global twanager_config
        twanager_config = config_in


@make_command()
def info(args):
    extend_plugins(twanager_config)
    return manage_info(args)



@make_command()
def addplugin(args):
    """Add the named plugin."""
    if args:
        for plugin_name in args:
            if _is_remote(plugin_name):
                short_name = _plugin_short_name(plugin_name)
            else:
                short_name = plugin_name
            try:
                __import__(short_name)
                print ('%s already installed, attempting to activate'
                        % short_name)
            except ImportError:
                print ('%s not yet installed, attempting to install'
                        % plugin_name)
                _install(plugin_name)
            except Exception, exc:
                usage('%s is present but errored out: %s' % (plugin_name, exc))
            _activate(short_name)
    else:
        usage('you need to name at least one plugin')


def _plugin_short_name(plugin_name):
    short_name = os.path.basename(urlparse.urlparse(plugin_name)[2])
    short_name = short_name[0:short_name.rindex('.py')]
    return short_name


def _is_remote(plugin_name):
    return (plugin_name.endswith('.py') and
            (plugin_name.startswith('http:') or
            plugin_name.startswith('https:')))


def _install(plugin_name):
    if _is_remote(plugin_name):
        _install_remote_file(plugin_name)
    else:
        _install_package(plugin_name)


def _install_package(plugin_name):
    usage('THIS FUNCTIONALITY IS NOT YET IMPLEMENTED')


def _install_remote_file(plugin_name):
    import urllib2
    remote_data = urllib2.urlopen(plugin_name)
    short_name = _plugin_short_name(plugin_name) + '.py'
    output = open(short_name, 'w')
    output.write(remote_data.read())
    remote_data.close()
    output.close()


def _activate(plugin_name):
    print 'activating %s' % plugin_name
    plugins = get_plugins(twanager_config)
    if plugin_name in plugins:
        usage('%s already activated' % plugin_name)
    else:
        try:
            plugin = __import__(plugin_name)
            getattr(plugin, 'init')
        except ImportError, exc:
            usage('%s will not import, not activating: %s' % (plugin_name, exc))
        except AttributeError, exc:
            usage('%s has no init, not a plugin, not activating' % plugin_name)
        except Exception, exc:
            usage('%s has unique error, not activating: %s' % (plugin_name, exc))
        append_plugin(twanager_config, plugin_name)


def append_plugin(config, plugin_name):
    plugin_file = config.get('plugin_file', 'extra_plugins')
    # Let IO Errors raise.
    pfile = open(plugin_file, 'w')
    pfile.write('%s\n' % plugin_name)


def get_plugins(config):
    plugin_file = config.get('plugin_file', 'extra_plugins')
    try:
        plugins = [line.strip() for line in open(plugin_file).readlines()
                if not line.startswith('#')]
    except IOError, exc:
        logging.warning('unable to read extra plugins file: %s' % exc)
        plugins = []
    return plugins


def extend_plugins(config):
    plugins = get_plugins(config)
    config['system_plugins'].extend(plugins)
