AUTHOR = 'Chris Dent'
AUTHOR_EMAIL = 'cdent@peermore.com'
NAME = 'tiddlywebplugins.prettyerror'
DESCRIPTION = 'TiddlyWeb plugin for customizable HTTP error messages'
VERSION = '0.5' # don't forget to update __init__.py too


import os

from setuptools import setup, find_packages


setup(
    namespace_packages = ['tiddlywebplugins'],
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    long_description = open(os.path.join(os.path.dirname(__file__), 'README')).read(),
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    url = 'http://pypi.python.org/pypi/%s' % NAME,
    platforms = 'Posix; MacOS X; Windows',
    packages = find_packages(exclude=['test']),
    install_requires = [
        'setuptools',
        'tiddlyweb>=1.1.0',
        'tiddlywebplugins.instancer',
        ],
    include_package_data = True,
    zip_safe = False,
    )
