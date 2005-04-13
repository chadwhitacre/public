# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

prefix=/usr/local

configure:
# delete and recreate the script to be installed
	rm -f zopeme
	cp zopeme.py zopeme
	chmod 555 zopeme

# delete and recreate the man page to be installed
	rm -f zopeme.1.gz
	gzip -c -9 zopeme.1 > zopeme.1.gz
	chmod 444 zopeme.1.gz

clean:
# delete the script and man page to be installed
	rm -rf zopeme zopeme.1.gz

install: configure
# after deleting and recreating the script and man page, install them
	install -C -o root -g wheel -m 555 zopeme ${prefix}/bin
	install -C -o root -g wheel -m 444 zopeme.1.gz ${prefix}/man/man1

uninstall:
# delete the script and man page from their installed locations
	rm -f ${prefix}/bin/zopeme
	rm -f ${prefix}/man/man1/zopeme.1.gz
