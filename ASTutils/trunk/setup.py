#!/usr/bin/env python
from distutils.core import setup

classifiers = [
    'Development Status :: 5 - Production/Stable'
  , 'Environment :: Other Environment'
  , 'Intended Audience :: Developers'
  , 'License :: Freeware'
  , 'Natural Language :: English'
  , 'Operating System :: OS Independent'
  , 'Programming Language :: Python'
  , 'Topic :: Software Development :: Libraries :: Python Modules'
                ]

setup( name = 'ASTutils'
     , version = '0.2'
     , package_dir = {'':'site-packages'}
     , packages = ['ASTutils']
     , description = 'ASTutils provides utilities for working with AST objects.'
     , author = 'Chad Whitacre'
     , author_email = 'chad [at] zetaweb [dot] com'
     , url = 'http://www.zetadev.com/software/'
     , classifiers = classifiers
      )
