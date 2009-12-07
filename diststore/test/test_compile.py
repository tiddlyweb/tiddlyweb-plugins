


def test_compile():
    try:
        import tiddlywebplugins.diststore
        assert True
    except ImportError, exc:
        assert False, exc
