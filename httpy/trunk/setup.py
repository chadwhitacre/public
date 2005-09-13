#!/usr/bin/env python
from distutils.core import setup
setup( name='httpy'
     , version=(0, 3)
     , package_dir={'':'site-packages'}
     , packages=[ 'httpy'
                , 'zope'
                , 'zope.interface'
                , 'zope.interface.common'
                , 'zope.server'
                , 'zope.server.ftp'
                , 'zope.server.http'
                , 'zope.server.interfaces'
                , 'zope.server.linereceiver'
                , 'zope.server.logger'
                 ]
      )