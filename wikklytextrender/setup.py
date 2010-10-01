
import os
from setuptools import setup, find_packages

VERSION = '0.8'

setup(
        namespace_packages = ['tiddlywebplugins'],
        name = 'tiddlywebplugins.wikklytextrender',
        version = VERSION,
        description = 'A TiddlyWeb plugin to render TiddlyWiki markup to HTML, server-side.',
        long_description=file(os.path.join(os.path.dirname(__file__), 'README')).read(),
        author = 'Chris Dent',
        url = 'http://pypi.python.org/pypi/tiddlywebplugins.wikklytextrender',
        packages = find_packages(exclude=['test', 'twp']),
        author_email = 'cdent@peermore.com',
        platforms = 'Posix; MacOS X; Windows',
        install_requires = ['setuptools', 'tiddlyweb', 'wikklytext'],
        zip_safe = False,
        )
