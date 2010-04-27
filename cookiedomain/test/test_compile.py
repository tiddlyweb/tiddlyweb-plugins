


def test_compile():
    try:
        import tiddlywebplugins.cookiedomain
        assert True
    except ImportError, exc:
        assert False, exc
