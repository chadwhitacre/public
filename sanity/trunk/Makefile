# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.


# set a default prefix if one wasn't specified on the command line
prefix?=/usr/local

configure:
# delete and recreate the script to be installed
	rm -f sanity
	cp sanity.py sanity
	chmod 555 sanity

# delete and recreate the man pages to be installed
	rm -f sanity.1.gz sanity.conf.5.tgz
	gzip -c -9 sanity.1 > sanity.1.gz
	gzip -c -9 sanity.conf.5 > sanity.conf.5.gz
	chmod 444 sanity.1.gz sanity.conf.5.gz

clean:
# delete the script and man page to be installed
	rm -rf sanity sanity.1.gz sanity.conf.5.gz

install: configure
# after deleting and recreating the script and man page, install them
	install -C -o root -g wheel -m 555 sanity ${prefix}/bin
	install -C -o root -g wheel -m 444 sanity.1.gz ${prefix}/man/man1
	install -C -o root -g wheel -m 444 sanity.conf.5.gz ${prefix}/man/man5

uninstall:
# delete the script and man page from their installed locations
	rm -f ${prefix}/bin/sanity
	rm -f ${prefix}/man/man1/sanity.1.gz
	rm -f ${prefix}/man/man5/sanity.conf.5.gz
