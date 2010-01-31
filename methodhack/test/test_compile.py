
def test_compile():
    try:
        import tiddlywebplugins.methodhack
        assert True
    except ImportError, exc:
        assert False, exc
