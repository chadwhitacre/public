# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

prefix=/usr/local

configure:
# delete and recreate the script to be installed
	rm -f svnextfinder
	cp svnextfinder.py svnextfinder
	chmod 555 svnextfinder

# delete and recreate the man page to be installed
	rm -f svnextfinder.1.gz
	gzip -c -9 svnextfinder.1 > svnextfinder.1.gz
	chmod 444 svnextfinder.1.gz

clean:
# delete the script and man page to be installed
	rm -rf svnextfinder svnextfinder.1.gz

install: configure
# after deleting and recreating the script and man page, install them
	install -C -o root -g wheel -m 555 svnextfinder ${prefix}/bin
	install -C -o root -g wheel -m 444 svnextfinder.1.gz ${prefix}/man/man1

uninstall:
# delete the script and man page from their installed locations
	rm -f ${prefix}/bin/svnextfinder
	rm -f ${prefix}/man/man1/svnextfinder.1.gz
