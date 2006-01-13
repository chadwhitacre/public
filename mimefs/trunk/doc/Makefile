# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

prefix=/usr/local


build:
	rm -f mimed.1.gz
	gzip -c -9 mimed.1 > mimed.1.gz
	chmod 444 mimed.1.gz

clean:
	rm -f mimed.1.gz

install: build

	install -C -o root -g wheel -m 444 mimed.1.gz ${prefix}/man/man1

uninstall:
	rm -f ${prefix}/man/man1/mimed.1.gz
