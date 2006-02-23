# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

prefix=/usr/local
version=0.9


configure:
# create the script to be installed
	rm -f httpy
	cp bin/httpy.py httpy
	chmod 555 httpy

# [re]create the man page to be installed
	rm -f httpy.1.gz
	gzip -c -9 doc/httpy.1 > httpy.1.gz
	chmod 444 httpy.1.gz


clean:
# remove all of the cruft that gets auto-generated on doc/install/release
	rm -f httpy httpy.1.gz
	rm -rf build
	rm -rf dist
	find . -name \*.pyc | xargs rm
	make -C doc/tex clean


install: configure
	install -o root -m 555 httpy ${prefix}/bin
	install -o root -m 444 httpy.1.gz ${prefix}/man/man1
	python setup.py install


uninstall:
	rm -f ${prefix}/bin/httpy
	rm -f ${prefix}/man/man1/httpy.1.gz




# Target for building a distribution
# ==================================

dist: clean
	mkdir dist
	mkdir dist/httpy-${version}
	cp -r Makefile README bin site-packages setup.py dist/httpy-${version}

	make -C doc/tex html pdf clean
	mkdir dist/httpy-${version}/doc
	cp -r doc/html doc/httpy* dist/httpy-${version}/doc

	find dist/httpy-${version} -name \.svn | xargs rm -r
	tar --directory dist -zcf dist/httpy-${version}.tgz httpy-${version}
	tar --directory dist -jcf dist/httpy-${version}.tbz httpy-${version}

# ZIP archive gets different line endings and script name
	svneol clean -w dist/httpy-${version}
	mv dist/httpy-${version}/bin/httpy.py dist/httpy-${version}/bin/httpy
	cd dist && zip -9rq httpy-${version}.zip httpy-${version}
#	rm -rf dist/httpy-${version}



# Target for updating Zope packages
# =================================
# This is not robust.

zope_svn_root=svn://svn.zope.org/repos/main/Zope3/tags/Zope-3.1.0/src/zope

zope: clean
# Update our zope packages from zope svn
	cp -r ./site-packages/httpy/_zope ./_zope
	echo ${zope_svn_root} > ./_zope/VERSION
	find _zope -name \*.py -exec sed -e 's/httpy._zope/HTTPY-ZOPE/g' -i '' {} \;
	svn export ${zope_svn_root}/interface ./_zope/interface --force
	svn export ${zope_svn_root}/server ./_zope/server --force
	find _zope -name \*.py -exec sed -e 's/zope/httpy._zope/g' -i '' {} \;
	find _zope -name \*.py -exec sed -e 's/HTTPY-ZOPE/httpy._zope/g' -i '' {} \;
	rm -rf ./site-packages/httpy/_zope
	mv ./_zope ./site-packages/httpy/
