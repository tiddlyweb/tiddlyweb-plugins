


def test_compile():
    try:
        import tiddlywebplugins.s5
        assert True
    except ImportError, exc:
        assert False, exc
