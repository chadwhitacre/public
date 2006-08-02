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

setup( name = 'httpyd'
     , version = '0.1'
     , package_dir = {'':'site-packages'}
     , packages = [ 'httpyd'
                   ]
     , scripts = [ 'bin/httpyd'
                 , 'bin/hinfo'
                  ]
     , description = 'httpyd is a robust and sane Python webserver.'
     , author = 'Chad Whitacre'
     , author_email = 'chad@zetaweb.com'
     , url = 'http://www.zetadev.com/software/httpyd/'
     , classifiers = classifiers
      )
