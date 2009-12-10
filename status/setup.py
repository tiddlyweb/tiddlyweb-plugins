
import os
from setuptools import setup, find_packages

VERSION = '0.4'

setup(
        namespace_packages = ['tiddlywebplugins'],
        name = 'tiddlywebplugins.status',
        version = VERSION,
        description = 'A TiddlyWeb plugin that provides information on the current user.',
        long_description=file(os.path.join(os.path.dirname(__file__), 'README')).read(),
        author = 'Chris Dent',
        url = 'http://pypi.python.org/pypi/tiddlywebplugins.status',
        packages = find_packages(exclude=['test']),
        author_email = 'cdent@peermore.com',
        platforms = 'Posix; MacOS X; Windows',
        install_requires = ['setuptools', 'tiddlyweb'],
        zip_safe = False,
        )
