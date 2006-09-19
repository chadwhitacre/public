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
  , 'Topic :: Internet :: WWW/HTTP :: HTTP Servers'
                ]

setup( name = 'aspen'
     , version = '0.1'
     , package_dir = {'':'site-packages'}
     , packages = [ 'aspen'
                   ]
     , scripts = [ 'bin/aspen'
                 , 'bin/hinfo'
                  ]
     , description = 'aspen is a robust and sane Python webserver.'
     , author = 'Chad Whitacre'
     , author_email = 'chad@zetaweb.com'
     , url = 'http://www.zetadev.com/software/aspen/'
     , classifiers = classifiers
      )
