


def test_compile():
    try:
        import tiddlywebplugins.reflector
        assert True
    except ImportError, exc:
        assert False, exc
