NAME=www.acn-us.org
FREEZE_FLAGS =  -o build
FREEZE=${APP_HOME}/usr/src/Python-2.4.3/Tools/freeze/freeze.py ${FREEZE_FLAGS}

all:
	python bin/fs2py.py www
	mv www.py site-packages/acn/
	python ${FREEZE} bin/${NAME}.py
	sed -e 's| ../../lib| ../usr/lib|g' -i '' build/Makefile
	make -C build
	cp -f build/${NAME} bin/${NAME}

dist:
	bzip2 -v -c bin/${NAME} > ${NAME}.bz2
	chmod +x www.acn-us.org.bz2
	scp www.acn-us.org.bz2 ferat:~

clean:
	find . -name \*.pyc -exec rm {} \;
	rm -rf build \
		   bin/${NAME} \
		   ${NAME}.bz2 \
		   site-packages/acn/www.py
