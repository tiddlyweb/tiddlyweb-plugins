


def test_compile():
    try:
        import tiddlywebplugins.templates
        assert True
    except ImportError, exc:
        assert False, exc
