
import os
from setuptools import setup, find_packages

VERSION = '0.5'

setup(
        namespace_packages = ['tiddlywebplugins'],
        name = 'tiddlywebplugins.pathinfohack',
        version = VERSION,
        description = 'A TiddlyWeb plugin providing support for / in entity names under Apache.',
        long_description=file(os.path.join(os.path.dirname(__file__), 'README')).read(),
        author = 'Oveek',
        url = 'http://pypi.python.org/pypi/tiddlywebplugins.pathinfohack',
        packages = find_packages(exclude=['test']),
        author_email = 'tiddlyweb@peermore.com',
        platforms = 'Posix; MacOS X; Windows',
        install_requires = ['setuptools', 'tiddlyweb>=0.9.92'],
        include_package_data = True,
        zip_safe=False,
        )
