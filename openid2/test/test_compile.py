


def test_compile():
    try:
        import tiddlywebplugins.openid2
        assert True
    except ImportError, exc:
        assert False, exc
