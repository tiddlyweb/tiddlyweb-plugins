


def test_compile():
    try:
        import tiddlywebplugins.tiddlywebweb
        assert True
    except ImportError, exc:
        assert False, exc
