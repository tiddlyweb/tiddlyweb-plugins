


def test_compile():
    try:
        import tiddlywebplugins.hashmaker
        assert True
    except ImportError, exc:
        assert False, exc
