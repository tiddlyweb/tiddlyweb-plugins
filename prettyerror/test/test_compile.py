


def test_compile():
    try:
        import tiddlywebplugins.prettyerror
        assert True
    except ImportError, exc:
        assert False, exc
