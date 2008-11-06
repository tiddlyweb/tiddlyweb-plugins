
TIDDLYBASE=/Users/cdent/src/tiddlywiki/association/serversides/tiddlyweb/core
PLUGINDIR=/Users/cdent/sc/tiddlywiki/contributors/ChrisDent/experimental/tiddlyweb-plugins

links: baselinks googlelinks pluginlinks

baselinks: lib tiddlyweb urls.map
	for file in $^; do \
		ln -s $(TIDDLYBASE)/$$file . ; \
	done

googlelinks: app.yaml google_user_challenger.py google_user_extractor.py googledata.py main.py tiddlywebconfig.py 
	for file in $^; do \
		ln -s $(PLUGINDIR)/googleappengine/$$file . ; \
	done

pluginlinks: atom twoter/twoter.py twoter/user.html twoter/bookmarklet.html
	for file in $^; do \
		ln -s $(PLUGINDIR)/$$file . ; \
	done

.DEFAULT:
	echo $@
