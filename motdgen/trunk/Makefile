# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.


# set a default prefix if one wasn't specified on the command line
prefix?=/usr/local

configure:
# delete and recreate the script to be installed
	rm -f motdgen
	cp motdgen.py motdgen
	chmod 555 motdgen

# delete and recreate the man page to be installed
	rm -f motdgen.1.gz
	gzip -c -9 motdgen.1 > motdgen.1.gz
	chmod 444 motdgen.1.gz

clean:
# delete the script and man page to be installed
	rm -rf motdgen motdgen.1.gz

install: configure
# after deleting and recreating the script and man page, install them
	install -C -o root -g wheel -m 555 motdgen ${prefix}/bin
	install -C -o root -g wheel -m 444 motdgen.1.gz ${prefix}/man/man1
	install -C -o root -g wheel -m 444 chad3d.flf ${prefix}/share/figlet

uninstall:
# delete the script and man page from their installed locations
	rm -f ${prefix}/bin/motdgen
	rm -f ${prefix}/man/man1/motdgen.1.gz
	rm -f ${prefix}/share/figlet/chad3d.flf

test: install
# install, spit out an example, and then show the man page
	motdgen foo.example.com I serve something-or-other.
	man motdgen
