# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

prefix=/usr/local

configure:
# delete and recreate the script to be installed
	rm -f httpy
	cp httpy.py httpy
	chmod 555 httpy

# delete and recreate the man page to be installed
	rm -f httpy.1.gz
	rm -f httpy.conf.5.gz
	gzip -c -9 httpy.1 > httpy.1.gz
	gzip -c -9 httpy.conf.5 > httpy.conf.5.gz
	chmod 444 httpy.1.gz
	chmod 444 httpy.conf.5.gz

clean:
# delete the script and man page to be installed
	rm -rf httpy httpy.1.gz httpy.conf.5.gz
	find . -name \*.pyc -exec rm -f {} \;

install: configure
# after deleting and recreating the script and man page, install them
	install -C -o root -g wheel -m 555 httpy ${prefix}/bin
	install -C -o root -g wheel -m 444 httpy.1.gz ${prefix}/man/man1
	install -C -o root -g wheel -m 444 httpy.conf.5.gz ${prefix}/man/man5

uninstall:
# delete the script and man page from their installed locations
	rm -f ${prefix}/bin/httpy
	rm -f ${prefix}/man/man1/httpy.1.gz
	rm -f ${prefix}/man/man5/httpy.conf.5.gz
