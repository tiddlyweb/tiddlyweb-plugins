
TIDDLYBASE=../tiddlyweb
FROM_SVN=../from-svn/fromsvn.py

infra: store
	./manager bag tiddlyweb < /dev/null
	./manager from_svn tiddlyweb http://svn.tiddlywiki.org/Trunk/verticals/tiddlywebclient/plugins/TiddlyWebAdaptorPlugin.js http://svn.tiddlywiki.org/Trunk/verticals/tiddlywebclient/plugins/TiddlyWebAutoSavePlugin.js http://svn.tiddlywiki.org/Trunk/verticals/tiddlywebclient/plugins/TiddlyWebSpowtDefaulterPlugin.js

store: links
	[ -d store ] || \
	mkdir -p store/bags &&  \
	mkdir store/recipes && \
	mkdir store/users

links:
	ln -s $(TIDDLYBASE)/tiddlyweb . || true
	ln -s $(TIDDLYBASE)/cherrypy . || true
	ln -s $(TIDDLYBASE)/lib . || true
	ln -s $(TIDDLYBASE)/urls.map . || true
	cp $(TIDDLYBASE)/manager . || true
	ln -s $(FROM_SVN) . || true
