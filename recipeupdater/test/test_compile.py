


def test_compile():
    try:
        import tiddlywebplugins.recipeupdater
        assert True
    except ImportError, exc:
        assert False, exc
