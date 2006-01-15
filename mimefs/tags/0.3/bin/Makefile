# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

prefix=/usr/local
user=mimefs
group=mimefs


configure:
	rm -f mimefsd
	cp mimefsd.py mimefsd
	chmod 500 mimefsd

clean:
	rm -rf mimefsd

install: configure
	install -C -o  ${user} -g ${group} -m 500 mimefsd ${prefix}/bin

uninstall:
	rm -f ${prefix}/bin/mimefsd
