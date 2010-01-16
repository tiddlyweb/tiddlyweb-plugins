"""
Test retrieving content from the TiddlyWiki Subversion repository.
"""

from tiddlywebplugins.twimport import _strip_extension


def test_strip_extension():

    actual = _strip_extension('foo.bar')
    expected = 'foo.bar'
    assert actual == expected

    actual = _strip_extension('foo.bar.js')
    expected = 'foo.bar'
    assert actual == expected

    actual = _strip_extension('foo.bar.baz.tid')
    expected = 'foo.bar.baz'
    assert actual == expected

    actual = _strip_extension('foo.bar')
    expected = 'foo.bar'
    assert actual == expected
