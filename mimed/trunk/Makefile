# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

prefix=/usr/local
db=/var/db/mime
user=mimedb
group=mimedb


configure:
# delete and recreate the script to be installed
	rm -f mimed
	cp bin/mimed.py mimed
	chmod 500 mimed


# delete and recreate the man page to be installed
	rm -f mimed.1.gz
	gzip -c -9 doc/mimed.1 > mimed.1.gz
	chmod 444 mimed.1.gz


clean:
# delete the script and man page to be installed
	rm -rf mimed mimed.1.gz build
	find . -name \*.pyc | xargs rm


install: configure
# installs the executable and man page, and sets up a database
# PostgreSQL should be installed but not running.
	python setup.py install

	install -C -o root -g wheel -m 500 mimed ${prefix}/bin
	install -C -o root -g wheel -m 444 mimed.1.gz ${prefix}/man/man1

	pw groupadd ${group}
	pw useradd ${user} -g ${group} -s /sbin/nologin

	mkdir ${db}
	chown ${user}:${group} ${db}
	sudo -u mimedb initdb ${db}

	echo 'a6d9b24e496c4255928b987995ac88b5' > /etc/mimedb.key
	chown ${user}:${group} /etc/mimedb.key
	chmod 400 /etc/mimedb.key


init:
# After you run make install, start postgres and hit this target.
	sudo -u ${user} psql postgres < init.psql


uninstall:
	rm -f ${prefix}/bin/mimed
	rm -f ${prefix}/man/man1/mimed.1.gz
	rm -rf /var/db/mime
	pw userdel ${user}
	#pw groupdel ${group} -- appears to be unnecessary?
