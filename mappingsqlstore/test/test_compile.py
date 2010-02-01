


def test_compile():
    try:
        import tiddlywebplugins.mappingsql
        assert True
    except ImportError, exc:
        assert False, exc
