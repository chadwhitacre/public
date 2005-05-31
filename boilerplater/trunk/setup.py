#!/usr/bin/env python
from distutils.core import setup

classifiers = [
    'Development Status :: 4 - Beta'
  , 'Environment :: Console'
  , 'Intended Audience :: Developers'
  , 'License :: Freely Distributable'
  , 'Natural Language :: English'
  , 'Operating System :: Unix'
  , 'Programming Language :: Python'
  , 'Topic :: Software Development :: Build Tools'
                ]
setup( name = 'boilerplater'
     , version = '0.1'
     , data_files=[('/usr/local/bin/', ['bin/boilerplater'])]
     , package_dir = {'':'site-packages'}
     , packages = ['Boilerplater', 'Boilerplater.Plugins']
     , description = 'Boilerplater adds boilerplate to a tree of files.'
     , author = 'Chad Whitacre'
     , author_email = 'chad [at] zetaweb [dot] com'
     , url = 'http://www.zetadev.com/software/boilerplater/'
     , classifiers = classifiers
      )
