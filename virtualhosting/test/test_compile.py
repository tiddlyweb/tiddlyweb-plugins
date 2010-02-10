


def test_compile():
    try:
        import tiddlywebplugins.virtualhosting
        assert True
    except ImportError, exc:
        assert False, exc
