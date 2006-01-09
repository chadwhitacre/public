# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

prefix=/usr/local

configure:
# delete and recreate the script to be installed
	rm -f mimed
	cp mimed.py mimed
	chmod 500 mimed

# delete and recreate the man page to be installed
	rm -f mimed.1.gz
	gzip -c -9 mimed.1 > mimed.1.gz
	chmod 444 mimed.1.gz

clean:
# delete the script and man page to be installed
	rm -rf mimed mimed.1.gz
	find . -name \*.pyc | xargs rm

install: configure
# after deleting and recreating the script and man page, install them
	install -C -o root -g wheel -m 500 mimed ${prefix}/bin
	install -C -o root -g wheel -m 444 mimed.1.gz ${prefix}/man/man1

uninstall:
# delete the script and man page from their installed locations
	rm -f ${prefix}/bin/mimed
	rm -f ${prefix}/man/man1/mimed.1.gz
