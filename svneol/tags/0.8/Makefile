# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

prefix=/usr/local

configure:
# delete and recreate the script to be installed
	rm -f svneol
	cp svneol.py svneol
	chmod 555 svneol

# delete and recreate the man page to be installed
	rm -f svneol.1.gz
	gzip -c -9 svneol.1 > svneol.1.gz
	chmod 444 svneol.1.gz

clean:
# delete the script and man page to be installed
	rm -rf svneol svneol.1.gz

install: configure
# after deleting and recreating the script and man page, install them
	install -C -o root -g wheel -m 555 svneol ${prefix}/bin
	install -C -o root -g wheel -m 444 svneol.1.gz ${prefix}/man/man1

uninstall:
# delete the script and man page from their installed locations
	rm -f ${prefix}/bin/svneol
	rm -f ${prefix}/man/man1/svneol.1.gz
