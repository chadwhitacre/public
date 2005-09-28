#!/usr/bin/env python
from distutils.core import setup

setup( name='httpy'
     , version="0.5"
     , package_dir={'':'site-packages'}
     , packages=[ 'httpy'
                , 'httpy._zope'
                , 'httpy._zope.interface'
                , 'httpy._zope.interface.common'
                , 'httpy._zope.server'
                , 'httpy._zope.server.ftp'
                , 'httpy._zope.server.http'
                , 'httpy._zope.server.interfaces'
                , 'httpy._zope.server.linereceiver'
                , 'httpy._zope.server.logger'
                , 'httpy._zope.server.tests'
                 ]
      )
