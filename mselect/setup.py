
import os
from setuptools import setup, find_packages

VERSION = '0.2'

setup(
        namespace_packages = ['tiddlywebplugins'],
        name = 'tiddlywebplugins.mselect',
        version = VERSION,
        description = 'A TiddlyWeb plugin providing a union select filter.',
        long_description=file(os.path.join(os.path.dirname(__file__), 'README')).read(),
        author = 'Chris Dent',
        url = 'http://pypi.python.org/pypi/tiddlywebplugins.mselect',
        packages = find_packages(exclude=['test']),
        author_email = 'cdent@peermore.com',
        platforms = 'Posix; MacOS X; Windows',
        install_requires = ['setuptools', 'tiddlyweb'],
        include_package_data = True,
        zip_safe=False,
        )
