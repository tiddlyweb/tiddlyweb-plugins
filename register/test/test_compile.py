


def test_compile():
    try:
        import tiddlywebplugins.register
        assert True
    except ImportError, exc:
        assert False, exc
