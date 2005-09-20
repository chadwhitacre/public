#!/usr/bin/env python
from distutils.core import setup
setup( name = 'zopepagetemplates'
     , version = "3.1.0c3"
     , package_dir = {'':'site-packages'}
     , packages = [ 'zope'
                  , 'zope.i18nmessageid'
                  , 'zope.pagetemplate'
                  , 'zope.tal'
                  , 'zope.tales'
                   ]
      )
