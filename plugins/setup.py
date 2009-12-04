
import os
from setuptools import setup, find_packages

VERSION = '0.2'

setup(
        namespace_packages = ['tiddlywebplugins'],
        name = 'tiddlywebplugins.plugins',
        version = VERSION,
        description = 'A TiddlyWeb plugin for flexibly managing system_plugins.',
        long_description=file(os.path.join(os.path.dirname(__file__), 'README')).read(),
        author = 'Chris Dent',
        url = 'http://pypi.python.org/pypi/tiddlywebplugins.plugins',
        packages = find_packages(exclude=['test']),
        author_email = 'cdent@peermore.com',
        platforms = 'Posix; MacOS X; Windows',
        install_requires = ['setuptools', 'tiddlyweb'],
        zip_safe=False
        )

