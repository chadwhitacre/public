# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

prefix=/usr/local

configure:
# Delete and recreate the script to be installed.
	rm -f httpy
	cp bin/httpy.py httpy
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
	rm -rf httpy httpy.1.gz httpy.conf.5.gz
	rm -rf build
	rm -rf dist
	find . -name \*.pyc -exec rm -f {} \;

install: configure
# After deleting and recreating the script and man page, install them.
	python setup.py install
	install -C -o root -g wheel -m 555 httpy ${prefix}/bin
	install -C -o root -g wheel -m 444 httpy.1.gz ${prefix}/man/man1
	install -C -o root -g wheel -m 444 httpy.conf.5.gz ${prefix}/man/man5

uninstall:
# Delete the script and man page from their installed locations/
# This should also remove the package from the python installation.
	rm -f ${prefix}/bin/httpy
	rm -f ${prefix}/man/man1/httpy.1.gz
	rm -f ${prefix}/man/man5/httpy.conf.5.gz
