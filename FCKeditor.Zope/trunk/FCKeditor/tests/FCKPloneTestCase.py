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
    app.fckc = app.portal.portal_fckconnector

    # create a couple users
    app.portal.acl_users._doAddUser('admin', 'secret', ['Manager'], [])
    app.portal.acl_users._doAddUser('user', 'secret', ['Member'], [])

    # login
    user = app.portal.acl_users.getUserById('admin').__of__(app.portal.acl_users)
    newSecurityManager(None, user)

    # set up some content
    app.portal.invokeFactory('Document', 'index_html', text="foo "*1000)
    app.portal.invokeFactory('Folder', 'Docs')

    # logout and post changes
    noSecurityManager()
    get_transaction().commit()

    ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))

app = ZopeTestCase.app()
customizePlone(app)
ZopeTestCase.close(app)
