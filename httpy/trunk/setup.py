#!/usr/bin/env python
from distutils.core import setup

classifiers = [
    'Development Status :: 4 - Beta'
  , 'Environment :: Console'
  , 'Intended Audience :: Developers'
  , 'License :: Freeware'
  , 'Natural Language :: English'
  , 'Operating System :: MacOS :: MacOS X'
  , 'Operating System :: Microsoft :: Windows'
  , 'Operating System :: POSIX'
  , 'Programming Language :: Python'
  , 'Topic :: Internet :: WWW/HTTP'
  , 'Topic :: Software Development :: Libraries :: Python Modules'
                ]

setup( name='httpy'
     , version="0.9"
     , package_dir={'':'site-packages'}
     , packages=[ 'httpy'
                , 'httpy._zope'
                , 'httpy._zope.interface'
                , 'httpy._zope.interface.common'
                , 'httpy._zope.server'
                #, 'httpy._zope.server.ftp'
                , 'httpy._zope.server.http'
                , 'httpy._zope.server.interfaces'
                , 'httpy._zope.server.linereceiver'
                , 'httpy._zope.server.logger'
                #, 'httpy._zope.server.tests'
                , 'httpy.couplers'
                , 'httpy.couplers.cgi'
                , 'httpy.couplers.fastcgi'
                , 'httpy.couplers.fastcgi.jon'
                , 'httpy.couplers.standalone'
                , 'httpy.responders'
                , 'httpy.tests'
                 ]
     , description = 'httpy is a sane and robust HTTP library for Python.'
     , author = 'Chad Whitacre'
     , author_email = 'chad@zetaweb.com'
     , url = 'http://www.zetadev.com/software/httpy/'
     , classifiers = classifiers
      )
