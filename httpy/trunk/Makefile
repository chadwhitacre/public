# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

prefix=/usr/local
zope_svn_root=svn://svn.zope.org/repos/main/Zope3/tags/Zope-3.1.0/src/zope

configure:
# Delete and recreate the script to be installed.
	chmod 555 httpy

# Delete and recreate the man page to be installed.
	rm -f httpy.1.gz
	rm -f httpy.conf.5.gz
	gzip -c -9 doc/man/httpy.1 > httpy.1.gz
	gzip -c -9 doc/man/httpy.conf.5 > httpy.conf.5.gz
	chmod 444 httpy.1.gz
	chmod 444 httpy.conf.5.gz

clean:
# Delete the script and man page to be installed.
	rm -rf httpy.1.gz httpy.conf.5.gz
	rm -rf build
	rm -rf dist
	rm -rf doc/html
	rm -rf _zope
	find . -name \*.pyc -exec rm -f {} \;

install: configure
# After deleting and recreating the script and man page, install them.
	python setup.py install
	install -C -o root -g wheel -m 555 bin/httpy ${prefix}/bin
	install -C -o root -g wheel -m 444 httpy.1.gz ${prefix}/man/man1
	install -C -o root -g wheel -m 444 httpy.conf.5.gz ${prefix}/man/man5

uninstall:
# Delete the script and man page from their installed locations/
# This should also remove the package from the python installation.
	rm -f ${prefix}/bin/httpy
	rm -f ${prefix}/man/man1/httpy.1.gz
	rm -f ${prefix}/man/man5/httpy.conf.5.gz


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
