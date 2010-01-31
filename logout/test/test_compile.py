
def test_compile():
    try:
        import tiddlywebplugins.logout
        assert True
    except ImportError, exc:
        assert False, exc
