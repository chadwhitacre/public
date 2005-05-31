version=0.9

clean:
	rm -rf archives/
	find . -name \*.pyc | xargs rm

squeaky: clean
	rm -rf src/
	rm -rf skins/fckeditor_base
	svn up
	utils/base2zope.py

dist: clean
	mkdir archives
	mkdir archives/FCKeditor
	cp -r *.py *.txt Extensions skins tests www archives/FCKeditor
	find archives/FCKeditor -name \.svn | xargs rm -r
	tar --directory archives -zcf archives/FCKeditor-${version}.tgz FCKeditor
	tar --directory archives -jcf archives/FCKeditor-${version}.tbz FCKeditor
	svneol clean -w archives/FCKeditor
	cd archives && zip -9rq FCKeditor-${version}.zip FCKeditor
#	rm -rf archives/FCKeditor
