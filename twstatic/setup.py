
import os
from setuptools import setup, find_packages

VERSION = '1.0'

setup(
        namespace_packages = ['tiddlywebplugins'],
        name = 'tiddlywebplugins.static',
        version = VERSION,
        description = 'A TiddlyWeb plugin that handles delivery of static files over HTTP.',
        long_description=file(os.path.join(os.path.dirname(__file__), 'README')).read(),
        author = 'Chris Dent',
        url = 'http://pypi.python.org/pypi/tiddlywebplugins.static',
        packages = find_packages(exclude=['test']),
        author_email = 'cdent@peermore.com',
        platforms = 'Posix; MacOS X; Windows',
        install_requires = ['setuptools', 'httpexceptor', 'tiddlyweb>=1.3.0'],
        zip_safe = False,
        )
