"""
test given a path or url to tiddler get a Tiddler.
"""

SAMPLE_PLUGIN = 'test/samples/beta/buried/hole.js'
SAMPLE_META_PLUGIN = 'test/samples/alpha/plugins/aplugin.js'
SAMPLE_TID = 'test/samples/alpha/Welcome.tid'
SAMPLE_TIDDLER = 'test/samples/alpha/Greetings.tiddler'
SAMPLE_CSS = 'test/samples/tiddlyweb.css'
SAMPLE_PNG = 'test/samples/peermore.png'


from tiddlywebplugins.twimport import url_to_tiddler

def test_simple_plugin():
    tiddler = url_to_tiddler(SAMPLE_PLUGIN)
    
    assert tiddler.title == 'hole'
    assert 'systemConfig' in tiddler.tags
    assert 'alert("i\'m in a hole!");' in tiddler.text

def test_meta_plugin():
    tiddler = url_to_tiddler(SAMPLE_META_PLUGIN)

    assert tiddler.title == 'aplugin'
    assert 'excludeLists' in tiddler.tags

def test_tid():
    tiddler = url_to_tiddler(SAMPLE_TID)

    assert tiddler.title == 'Welcome'
    assert 'hello' in tiddler.tags
    assert 'goodbye' in tiddler.tags
    assert tiddler.modifier == 'cdent'
    assert '\nNever' in tiddler.text

def test_tiddler():
    tiddler = url_to_tiddler(SAMPLE_TIDDLER)

    assert tiddler.title == 'Greetings'
    assert 'Welcome to the real world' in tiddler.text

def test_css_tiddler():
    tiddler = url_to_tiddler(SAMPLE_CSS)

    assert tiddler.title == 'tiddlyweb.css'
    assert tiddler.type == 'text/css'

def test_png_tiddler():
    tiddler = url_to_tiddler(SAMPLE_PNG)

    assert tiddler.title == 'peermore.png'
    assert tiddler.type == 'image/png'
