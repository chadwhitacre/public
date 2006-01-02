#!/usr/bin/env python
from distutils.core import setup
setup( name = 'zpt'
     , version = "3.1.0"
     , package_dir = {'':'site-packages'}
     , packages = [ 'zpt'
                  , 'zpt._zope'
                  , 'zpt._zope.i18nmessageid'
                  , 'zpt._zope.pagetemplate'
                  , 'zpt._zope.tal'
                  , 'zpt._zope.tales'
                  , 'zpt._zope.tales'
                  , 'zpt._zope.tales'
                   ]
      )
