# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

prefix=/usr/local
version=0.9a2


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
	find . -name \*.pyc | xargs rm


install: configure
	install -o root -m 555 httpy ${prefix}/bin
	install -o root -m 444 httpy.1.gz ${prefix}/man/man1
	python setup.py install


uninstall:
	rm -f ${prefix}/bin/httpy
	rm -f ${prefix}/man/man1/httpy.1.gz
