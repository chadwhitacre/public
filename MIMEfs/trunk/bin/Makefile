# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

prefix=/usr/local
user=mimedb
group=mimedb


configure:
	rm -f mimed
	cp mimed.py mimed
	chmod 500 mimed

clean:
	rm -rf mimed

install: configure
	install -C -o  ${user} -g ${group} -m 500 mimed ${prefix}/bin

uninstall:
	rm -f ${prefix}/bin/mimed
