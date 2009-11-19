"""
Manage locating jinja2 templates in the tiddlywebplugins
package.
"""
from jinja2 import Environment, FileSystemLoader, PackageLoader, TemplateNotFound
template_env = None

def get_template(environ, template_name):
    """
    Get a template from the Jinja Environment. First try the file loader
    to get the template local to the instance running the code. If it isn't
    there, then try from the tiddlywebplugins package.
    """
    global template_env
    if not template_env:
        template_path = environ['tiddlyweb.config'].get('plugin_local_templates', 'templates')
        template_env = [
                Environment(loader=FileSystemLoader(template_path)),
                Environment(loader=PackageLoader('tiddlywebplugins.templates', 'templates'))
                ]
    index = 0
    while 1:
        try:
            env = template_env[index]
            template = env.get_template(template_name)
            return template
        except TemplateNotFound:
            index += 1
        except IndexError:
            raise TemplateNotFound(template_name)
