def test_compile():
    try:
        import tiddlywebplugins.twimport
        assert True
    except ImportError, exc:
        assert False, exc
