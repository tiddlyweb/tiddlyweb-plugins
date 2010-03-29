"""
Manage locating jinja2 templates in the tiddlywebplugins
package or a local templates dir.

Jinja2 uses a 'loader' to locate requests templates. This
package sets up two loaders, tried in sequence. The first
loader looks in the 'templates' directory in the current
TiddlyWeb instances. This directory name be overridden by
setting plugin_local_templates in tiddlywebconfig.py to
some path.

The second loader looks inside the tiddlywebplugins.templates
package. TiddlyWeb plugins can package default templates into
this location (see tiddlywebplugins.wimporter for an example).

If template is not found in either location, the jinja
TemplateNotFound exception is raised, replicating the standard
jinja behavior.
"""
import os
import urllib

from jinja2 import Environment, ChoiceLoader, FileSystemLoader, PackageLoader, TemplateNotFound
template_env = None

def uri(name):
    return urllib.quote(name.encode('utf-8'), safe='')

def get_template(environ, template_name):
    """
    Get a template from the Jinja Environment. First try the file loader
    to get the template local to the instance running the code. If it isn't
    there, then try from the tiddlywebplugins package.
    """
    global template_env
    if not template_env:
        template_path = environ['tiddlyweb.config'].get('plugin_local_templates', 'templates')
        if not os.path.isabs(template_path):
            template_path = os.path.join(environ['tiddlyweb.config'].get(
                'root_dir', ''), template_path)
        template_env = Environment(loader=ChoiceLoader([
            FileSystemLoader(template_path),
            PackageLoader('tiddlywebplugins.templates', 'templates')
            ]))
        template_env.filters['uri'] = uri
    return template_env.get_template(template_name)
