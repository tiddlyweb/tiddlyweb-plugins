


def test_compile():
    try:
        import tiddlywebplugins.socialusers
        assert True
    except ImportError, exc:
        assert False, exc
