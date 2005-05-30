# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

prefix=/usr/local

configure:
# delete and recreate the script to be installed
	rm -f licensor
	cp licensor.py licensor
	chmod 555 licensor

# delete and recreate the man page to be installed
	rm -f licensor.1.gz
	gzip -c -9 licensor.1 > licensor.1.gz
	chmod 444 licensor.1.gz

clean:
# delete the script and man page to be installed
	rm -rf licensor licensor.1.gz

install: configure
# after deleting and recreating the script and man page, install them
	install -C -o root -g wheel -m 555 licensor ${prefix}/bin
	install -C -o root -g wheel -m 444 licensor.1.gz ${prefix}/man/man1

uninstall:
# delete the script and man page from their installed locations
	rm -f ${prefix}/bin/licensor
	rm -f ${prefix}/man/man1/licensor.1.gz

test:
	./test.py
	rm -rf *.pyc