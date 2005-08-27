# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

prefix=/usr/local

configure:
# Delete and recreate the script to be installed.
	rm -f kraken
	cp kraken.py kraken
	chmod 555 kraken

# Delete and recreate the man page to be installed.
	rm -f kraken.1.gz
	rm -f kraken.conf.5.gz
	gzip -c -9 doc/man/kraken.1 > kraken.1.gz
	gzip -c -9 doc/man/kraken.conf.5 > kraken.conf.5.gz
	chmod 444 kraken.1.gz
	chmod 444 kraken.conf.5.gz

clean:
# Delete the script and man page to be installed.
	rm -rf kraken kraken.1.gz kraken.conf.5.gz
	rm -rf build
	rm -rf dist
	find . -name \*.pyc -exec rm -f {} \;

install: configure
# After deleting and recreating the script and man page, install them.
	python setup.py install
	install -C -o root -g wheel -m 555 kraken ${prefix}/bin
	install -C -o root -g wheel -m 444 kraken.1.gz ${prefix}/man/man1
	install -C -o root -g wheel -m 444 kraken.conf.5.gz ${prefix}/man/man5

uninstall:
# Delete the script and man page from their installed locations/
# This should also remove the package from the python installation.
	rm -f ${prefix}/bin/kraken
	rm -f ${prefix}/man/man1/kraken.1.gz
	rm -f ${prefix}/man/man5/kraken.conf.5.gz
