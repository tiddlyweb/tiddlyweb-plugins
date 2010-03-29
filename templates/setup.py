
import os
from setuptools import setup, find_packages

VERSION = '0.8'

setup(
        namespace_packages = ['tiddlywebplugins'],
        name = 'tiddlywebplugins.templates',
        version = VERSION,
        description = 'A TiddlyWeb plugin with tools and packaging for templates.',
        long_description=file(os.path.join(os.path.dirname(__file__), 'README')).read(),
        author = 'Chris Dent',
        url = 'http://pypi.python.org/pypi/tiddlywebplugins.templates',
        packages = find_packages(exclude=['test']),
        author_email = 'cdent@peermore.com',
        platforms = 'Posix; MacOS X; Windows',
        install_requires = ['setuptools', 'Jinja2'],
        include_package_data = True,
        zip_safe=False,
        )
