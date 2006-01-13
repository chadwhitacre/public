# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

prefix=/usr/local
db=/var/db/mimefs
user=mimefs
group=mimefs


build:
	make -C bin
	make -C doc
	python setup.py build


clean:
	make -C bin clean
	make -C doc clean
	rm -rf build
	find . -name \*.pyc | xargs rm


install: build

	pw groupadd ${group}
	pw useradd ${user} -g ${group} -s /sbin/nologin

	make -C bin install
	make -C doc install

	mkdir ${db}
	chown ${user}:${group} ${db}
	sudo -u mimedb initdb ${db}

	echo -n 'a6d9b24e496c4255928b987995ac88b5' > /etc/mimefs.key
	chown ${user}:${group} /etc/mimefs.key
	chmod 400 /etc/mimefs.key

	python setup.py install


init:
# After you run make install, start postgres and hit this target.
	sudo -u ${user} psql postgres < init.psql


uninstall:
	make -C bin uninstall
	make -C doc uninstall
	rm -rf ${db}
	pw userdel ${user}
	#pw groupdel ${group} -- appears to be unnecessary?
