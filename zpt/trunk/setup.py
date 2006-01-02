#!/usr/bin/env python
from distutils.core import setup
setup( name = 'zpt'
     , version = "1.0"
     , package_dir = {'':'site-packages'}
     , packages = [ 'zpt'
                  , 'zpt._pytz'
                  , 'zpt._pytz.zoneinfo'
                  , 'zpt._zope'
                  , 'zpt._zope.component'
                  , 'zpt._zope.i18n'
                  , 'zpt._zope.i18nmessageid'
                  , 'zpt._zope.interface'
                  , 'zpt._zope.pagetemplate'
                  , 'zpt._zope.schema'
                  , 'zpt._zope.tal'
                  , 'zpt._zope.tales'
                   ]
      )
