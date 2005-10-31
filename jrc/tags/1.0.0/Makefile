# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.


# set a default prefix if one wasn't specified on the command line
prefix?=/usr/local

configure:
# delete and recreate the script to be installed
	rm -f jrc
	cp jrc.py jrc
	chmod 555 jrc

# delete and recreate the man page to be installed
	rm -f jrc.1.gz
	gzip -c -9 jrc.1 > jrc.1.gz
	chmod 444 jrc.1.gz

clean:
# delete the script and man page to be installed
	rm -rf jrc jrc.1.gz

install: configure
# after deleting and recreating the script and man page, install them
	install -C -o root -g wheel -m 555 jrc ${prefix}/bin
	install -C -o root -g wheel -m 444 jrc.1.gz ${prefix}/man/man1

uninstall:
# delete the script and man page from their installed locations
	rm -f ${prefix}/bin/jrc
	rm -f ${prefix}/man/man1/jrc.1.gz
