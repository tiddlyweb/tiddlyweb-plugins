


def test_compile():
    try:
        import tiddlywebplugins.caching
        assert True
    except ImportError, exc:
        assert False, exc
