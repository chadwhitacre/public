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
