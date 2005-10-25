# (c) 2005 Chad Whitacre <http://www.zetadev.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

prefix=/usr/local

configure:
# delete and recreate the script to be installed
	rm -f bloodhound
	cp bloodhound.py bloodhound
	chmod 555 bloodhound

# delete and recreate the man page to be installed
	rm -f bloodhound.1.gz
	gzip -c -9 bloodhound.1 > bloodhound.1.gz
	chmod 444 bloodhound.1.gz

clean:
# remove installation cruft
	rm -rf bloodhound bloodhound.1.gz *.pyc build

install: configure
# after deleting and recreating the script and man page, install them
	python setup.py install
	install -C -o root -g wheel -m 555 bloodhound ${prefix}/bin
	install -C -o root -g wheel -m 444 bloodhound.1.gz ${prefix}/man/man1

uninstall:
# delete the script and man page from their installed locations
	rm -f ${prefix}/bin/bloodhound
	rm -f ${prefix}/man/man1/bloodhound.1.gz
	python setup.py uninstall
