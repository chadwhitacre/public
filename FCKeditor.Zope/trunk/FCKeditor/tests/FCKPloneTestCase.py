#BOILERPLATE###################################################################
#                                                                             #
#  This package wraps FCKeditor for use in the Zope web application server.   #
#  Copyright (C) 2005 Chad Whitacre < http://www.zetadev.com/ >               #
#                                                                             #
#  This library is free software; you can redistribute it and/or modify it    #
#  under the terms of the GNU Lesser General Public License as published by   #
#  the Free Software Foundation; either version 2.1 of the License, or (at    #
#  your option) any later version.                                            #
#                                                                             #
#  This library is distributed in the hope that it will be useful, but        #
#  WITHOUT ANY WARRANTY; without even the implied warranty of                 #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser    #
#  General Public License for more details.                                   #
#                                                                             #
#  You should have received a copy of the GNU Lesser General Public License   #
#  along with this library; if not, write to the Free Software Foundation,    #
#  Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA                #
#                                                                             #
#                                                                             #
###################################################################BOILERPLATE#
# Python
import time

# Zope/Plone
from AccessControl.SecurityManagement import newSecurityManager, \
                                             noSecurityManager
from Testing import ZopeTestCase

ZopeTestCase.installProduct('FCKeditor')

from Products.CMFPlone.tests import PloneTestCase

class FCKPloneTestCase(PloneTestCase.PloneTestCase):
    pass

def customizePlone(app):
    _start = time.time(); ZopeTestCase._print('Customizing Plone Site ... ')

    # install ourselves in Plone-space
    app.portal.portal_quickinstaller.installProduct('FCKeditor')

    # create a couple users
    app.portal.acl_users._doAddUser('admin', 'secret', ['Manager'], [])
    app.portal.acl_users._doAddUser('user', 'secret', ['Member'], [])

    # login
    user = app.portal.acl_users.getUserById('admin').__of__(app.portal.acl_users)
    newSecurityManager(None, user)

    # set up some content
    app.portal.invokeFactory('Document', 'index_html', text="foo "*1000)
    app.portal.invokeFactory('Folder', 'Docs')
    app.portal.Docs.invokeFactory('Folder', id='Test')
    app.portal.Docs.invokeFactory('Document', id='Doc')
    app.portal.Docs.invokeFactory('Image', id='Img')
    app.portal.Docs.invokeFactory('File', id='PDF')

    # logout and post changes
    noSecurityManager()
    get_transaction().commit()

    ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))

app = ZopeTestCase.app()
customizePlone(app)
ZopeTestCase.close(app)
