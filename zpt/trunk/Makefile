VERSION=Zope-3.1.0
SVN=svn export svn://svn.zope.org/repos/main/Zope3/tags/${VERSION}/src

dummy:
	echo "nothing to see"

download:
	mkdir -p site-packages/zpt/_zope
	${SVN}/pytz site-packages/zpt/_pytz
	${SVN}/zope/component site-packages/zpt/_zope/component
	${SVN}/zope/i18n site-packages/zpt/_zope/i18n
	${SVN}/zope/i18nmessageid site-packages/zpt/_zope/i18nmessageid
	${SVN}/zope/interface site-packages/zpt/_zope/interface
	${SVN}/zope/pagetemplate site-packages/zpt/_zope/pagetemplate
	${SVN}/zope/schema site-packages/zpt/_zope/schema
	${SVN}/zope/tal site-packages/zpt/_zope/tal
	${SVN}/zope/tales site-packages/zpt/_zope/tales
	${SVN}/zope/testing site-packages/zpt/_zope/testing

clean:
	rm -rf site-packages/zpt/_zope
