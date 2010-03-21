
def test_compile():
    try:
        import tiddlywebplugins.env
        assert True
    except ImportError, exc:
        assert False, exc

